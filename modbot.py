import os
import re
import logging, logging.config
import urllib2
from datetime import datetime, timedelta
from time import time

import reddit
# from imgcmp import ImageCompare, FuzzyImageCompare, Image
from StringIO import StringIO
from BeautifulSoup import BeautifulSoup
from sqlalchemy import func
from sqlalchemy.sql import and_
from sqlalchemy.sql.expression import desc
from sqlalchemy.orm.exc import NoResultFound

from models import cfg_file, path_to_cfg, db, Subreddit, Condition, \
    ActionLog, AutoReapproval

# global reddit session
r = None

# don't action any reports older than this
REPORT_BACKLOG_LIMIT = timedelta(days=2)

# minimum image similarity to consider it as a match
MIN_IMAGE_SIMILARITY = 45


def perform_action(subreddit, item, condition):
    """Performs the action for the condition(s).
    
    Also delivers the comment (if set) and creates an ActionLog entry.
    """
    
    global r
    comment = None
    disclaimer = ('\n\n*I am a bot, and this action was performed '
                    'automatically. Please [contact the moderators of this '
                    'subreddit](http://www.reddit.com/message/compose?'
                    'to=%23'+item.subreddit.display_name+') if you have any '
                    'questions or concerns.*')

    # build the comment if multiple conditions were matched
    if isinstance(condition, list):
        # build short reason string for modporn submission later
        short_reason = ' '.join(['['+c.short_reason+']' for c in condition
                                 if c.short_reason is not None])

        if any([c.comment for c in condition]):
            if condition[0].action == 'alert':
                verb = 'alerted'
            else:
                verb = condition[0].action+'d'

            comment = ('Unfortunately, your submission has been '+verb+' for the following reasons:\n\n')
            for c in condition:
                if c.comment:
                    comment += '* '+c.comment+'\n'
            comment += ('\nFor more information regarding these issues please '
                        ' [see the FAQ](http://www.reddit.com/r/'+
                        item.subreddit.display_name+'/faq), and feel '
                        'free to resubmit once they have been resolved. '
                        'Thank you!')

        # bit of a hack and only logs and uses attributes from first
        # condition matched, should find a better method
        condition = condition[0]
    else:
        short_reason = condition.short_reason
        comment = condition.comment

    # abort if it's an alert and we've already alerted on this item
    if condition.action == 'alert':
        try:
            ActionLog.query.filter(
                and_(ActionLog.permalink == get_permalink(item),
                     ActionLog.action == 'alert')).one()
            return
        except NoResultFound:
            pass

    # perform the action
    if condition.action == 'remove':
        item.remove(condition.spam)
    elif condition.action == 'approve':
        item.approve()
    elif condition.action == 'set_flair':
        item.set_flair(condition.set_flair_text,
                       condition.set_flair_class)

    # deliver the comment if set
    if comment:
        if condition.comment_method == 'comment':
            post_comment(item, comment+disclaimer)
        elif condition.comment_method == 'modmail':
            r.compose_message('#'+subreddit.name,
                              'AutoModerator condition matched',
                              get_permalink(item)+'\n\n'+comment)
        elif condition.comment_method == 'message':
            r.compose_message(item.author.name,
                              'AutoModerator condition matched',
                              get_permalink(item)+'\n\n'+comment+disclaimer)

    # log the action taken
    action_log = ActionLog()
    action_log.subreddit_id = subreddit.id
    action_log.user = item.author.name
    action_log.permalink = get_permalink(item)
    action_log.created_utc = datetime.utcfromtimestamp(item.created_utc)
    action_log.action_time = datetime.utcnow()
    action_log.action = condition.action
    action_log.matched_condition = condition.id

    if isinstance(item, reddit.objects.Submission):
        action_log.title = item.title
        action_log.url = item.url
        action_log.domain = item.domain
#         logging.info('  /r/%s: %s submission "%s"',
#                         subreddit.name,
#                         condition.action,
#                         item.title.encode('ascii', 'ignore'))
        logging.info('  /r/%s: %s submission "%s"',
                        subreddit.name,
                        condition.action,
                        item.title)
    elif isinstance(item, reddit.objects.Comment):
        logging.info('  /r/%s: %s comment by user %s',
                        subreddit.name,
                        condition.action,
                        item.author.name)

    db.session.add(action_log)
    db.session.commit()

    # SFWPorn network moderation requirements
    # NO LONGER NEEDED
#     if (isinstance(item, reddit.objects.Submission) and
#             condition.action == 'remove' and
#             short_reason is not None):
#         # submit to ModerationPorn
#         r.submit('ModerationPorn',
#                 '['+subreddit.name+'] '+
#                 '['+item.author.name+'] '+
#                 item.title+
#                 ' '+short_reason,
#                 url=item.permalink)

    if (isinstance(item, reddit.objects.Submission) and
            condition.action == 'remove' and
            comment):
        # send them a PM as well
        r.compose_message(item.author.name,
                'SFWPorn submission removed',
                get_permalink(item)+'\n\n'+comment+disclaimer)


def post_comment(item, comment):
    """Posts a distinguished comment as a reply to an item."""
    if isinstance(item, reddit.objects.Submission):
        response = item.add_comment(comment)
        response.distinguish()
    elif isinstance(item, reddit.objects.Comment):
        response = item.reply(comment)
        response.distinguish()


def check_items(name, items, sr_dict, stop_time):
    """Checks the items generator for any matching conditions."""
    item_count = 0
    skip_count = 0
    skip_subs = set()
    start_time = time()
    seen_subs = set()

    logging.info('Checking new %ss', name)

    try:
        for item in items:
            # skip any items in /new that have been approved
            if name == 'submission' and item.approved_by:
                continue
    
            item_time = datetime.utcfromtimestamp(item.created_utc)
            if item_time <= stop_time:
                break
    
            try:
                subreddit = sr_dict[item.subreddit.display_name.lower()]
            except KeyError:
                skip_count += 1
                skip_subs.add(item.subreddit.display_name.lower())
                continue
    
            conditions = (subreddit.conditions
                            .filter(Condition.parent_id == None)
                            .all())
            conditions += (Condition.query.filter(
                           and_(Condition.subreddit_id == None,
                                Condition.parent_id == None))
                           .all())
            conditions = filter_conditions(name, conditions)
    
            item_count += 1
    
            if subreddit.name not in seen_subs:
                setattr(subreddit, 'last_'+name, item_time)
                seen_subs.add(subreddit.name)
    
            # check removal conditions, stop checking if any matched
            if check_conditions(subreddit, item,
                    [c for c in conditions if c.action == 'remove']):
                continue
    
            # check set_flair conditions 
            check_conditions(subreddit, item,
                    [c for c in conditions if c.action == 'set_flair'])
    
            # check approval conditions
            check_conditions(subreddit, item,
                    [c for c in conditions if c.action == 'approve'])
    
            # check alert conditions
            check_conditions(subreddit, item,
                    [c for c in conditions if c.action == 'alert'])
    
            # if doing reports, check auto-reapproval if enabled
            if (name == 'report' and subreddit.auto_reapprove and
                    item.approved_by is not None):
                try:
                        # see if this item has already been auto-reapproved
                    entry = (AutoReapproval.query.filter(
                            AutoReapproval.permalink == get_permalink(item))
                            .one())
                    in_db = True
                except NoResultFound:
                    entry = AutoReapproval()
                    entry.subreddit_id = subreddit.id
                    entry.permalink = get_permalink(item)
                    entry.original_approver = item.approved_by.name
                    entry.total_reports = 0
                    entry.first_approval_time = datetime.utcnow()
                    in_db = False
    
                if (in_db or item.approved_by.name !=
                        cfg_file.get('reddit', 'username')):
                    item.approve()
                    entry.total_reports += item.num_reports
                    entry.last_approval_time = datetime.utcnow()
    
                    db.session.add(entry)
                    db.session.commit()
                    logging.info('  Re-approved %s', entry.permalink)
                            
        db.session.commit()
    except Exception as e:
        logging.error('  ERROR: %s', e)
        db.session.rollback()

    logging.info('  Checked %s items, skipped %s items in %s (skips: %s)',
            item_count, skip_count, elapsed_since(start_time),
            ', '.join(skip_subs))


def filter_conditions(name, conditions):
    """Filters a list of conditions based on the queue's needs."""
    if name == 'spam':
        return [c for c in conditions if c.num_reports == None]
    elif name == 'report':
        return [c for c in conditions if c.num_reports is not None and
                c.is_shadowbanned != True]
    elif name == 'submission':
        return [c for c in conditions if c.action != 'approve' and
                c.num_reports == None and c.is_shadowbanned != True]
    elif name == 'comment':
        return [c for c in conditions if c.action != 'approve' and
                c.num_reports == None and c.is_shadowbanned != True]


def check_conditions(subreddit, item, conditions):
    """Checks an item against a set of conditions.

    Returns the first condition that matches, or a list of all conditions that
    match if check_all_conditions is set on the subreddit. Returns None if no
    conditions match.
    """
    if isinstance(item, reddit.objects.Submission):
        conditions = [c for c in conditions
                          if c.subject == 'submission' or
                             c.subject == 'both']
#         logging.debug('      Checking submission titled "%s"',
#                         item.title.encode('ascii', 'ignore'))
        logging.debug('      Checking submission titled "%s"',
                        item.title)
    elif isinstance(item, reddit.objects.Comment):
        conditions = [c for c in conditions
                          if c.subject == 'comment' or
                             c.subject == 'both']
        logging.debug('      Checking comment by user %s',
                        item.author.name)

    # sort the conditions so the easiest ones are checked first
    conditions.sort(key=condition_complexity)
    matched = list()

    for condition in conditions:
        try:
            match = check_condition(item, condition)
        except:
            match = False

        if match:
            if subreddit.check_all_conditions:
                matched.append(condition)
            else:
                perform_action(subreddit, item, condition)
                return condition

    if subreddit.check_all_conditions and len(matched) > 0:
        perform_action(subreddit, item, matched)
        return matched
    return None


def check_condition(item, condition):
    """Checks an item against a single condition (and sub-conditions).
    
    Returns True if it matches, or False if not
    """
    start_time = time()

    if condition.attribute == 'user':
        if item.author:
            test_string = item.author.name
    elif (condition.attribute == 'body' and
            isinstance(item, reddit.objects.Submission)):
        test_string = item.selftext
    elif condition.attribute.startswith('media_'):
        if item.media:
            try:
                if condition.attribute == 'media_user':
                    test_string = item.media['oembed']['author_name']
                elif condition.attribute == 'media_title':
                    test_string = item.media['oembed']['description']
                elif condition.attribute == 'media_description':
                    test_string = item.media['oembed']['description']
            except KeyError:
                test_string = ''
        else:
            test_string = ''
    elif condition.attribute == 'meme_name':
        test_string = get_meme_name(item)
#     elif condition.attribute == 'similar_image':
#         test_string = most_similar_image(item)
    else:
        test_string = getattr(item, condition.attribute)
    if not test_string:
        test_string = ''

    if condition.inverse:
#         logging.debug('        Check #%s: "%s" NOT match ^%s$',
#                         condition.id,
#                         test_string.encode('ascii', 'ignore'),
#                         condition.value.encode('ascii', 'ignore').lower())
        logging.debug('        Check #%s: "%s" NOT match ^%s$',
                        condition.id,
                        test_string,
                        condition.value.lower())
    else:
#         logging.debug('        Check #%s: "%s" match ^%s$',
#                         condition.id,
#                         test_string.encode('ascii', 'ignore'),
#                         condition.value.encode('ascii', 'ignore').lower())
        logging.debug('        Check #%s: "%s" match ^%s$',
                        condition.id,
                        test_string,
                        condition.value.lower())

    if re.search('^'+condition.value.lower()+'$',
            test_string.lower(),
            re.DOTALL|re.UNICODE):
        satisfied = True
    else:
        satisfied = False

    # flip the result it's an inverse condition
    if condition.inverse:
        satisfied = not satisfied

    # check number of reports if necessary
    if satisfied and condition.num_reports is not None:
        if condition.auto_reapproving != False:
            # get number of reports already cleared
            try:
                entry = (AutoReapproval.query.filter(
                         AutoReapproval.permalink == get_permalink(item))
                        .one())
                previous_reports = entry.total_reports
            except NoResultFound:
                previous_reports = 0
            total_reports = item.num_reports + previous_reports
        else:
            total_reports = item.num_reports

        satisfied = (total_reports >= condition.num_reports)
    elif satisfied and condition.num_reports is None:
        satisfied = (item.num_reports == 0)

    # check user conditions if necessary
    if satisfied:
        satisfied = check_user_conditions(item, condition)
        logging.debug('          User condition result = %s', satisfied)

    # make sure all sub-conditions are satisfied as well
    if satisfied:
        if condition.additional_conditions:
            logging.debug('        Checking sub-conditions:')
        for sub_condition in condition.additional_conditions:
            match = check_condition(item, sub_condition)
            if not match:
                satisfied = False
                break
        if condition.additional_conditions:
            logging.debug('        Sub-condition result = %s', satisfied)

    logging.debug('        Result = %s in %s',
                    satisfied, elapsed_since(start_time))
    return satisfied


def check_user_conditions(item, condition):
    """Checks an item's author against the age/karma/has-gold requirements."""
    # if no user conditions are set, no need to check at all
    if (condition.is_gold is None and
            condition.is_shadowbanned is None and
            condition.link_karma is None and
            condition.comment_karma is None and
            condition.combined_karma is None and
            condition.account_age is None and
            condition.account_rank is None):
        return True

    # returning True will result in the action being performed
    # so when removing or alerting, return True if they DON'T meet user reqs
    # but for approving and flair we return True if they DO meet it
    if condition.action in ['remove', 'alert']:
        fail_result = True
    elif condition.action in ['approve', 'set_flair']:
        fail_result = False

    # if they deleted the post, fail user checks
    if not item.author:
        return fail_result

    # user rank check
    if condition.account_rank is not None:
        if not user_has_rank(item.subreddit, item.author,
                            condition.account_rank):
            return fail_result

    # shadowbanned check
    if condition.is_shadowbanned is not None:
        user = item.reddit_session.get_redditor(item.author, fetch=False)
        try: # try to get user overview
            list(user.get_overview(limit=1))
        except: # if that failed, they're probably shadowbanned
            return fail_result

    # get user info
    user = item.reddit_session.get_redditor(item.author)

    # reddit gold check
    if condition.is_gold is not None:
        if condition.is_gold != user.is_gold:
            return fail_result

    # karma checks
    if condition.link_karma is not None:
        if user.link_karma < condition.link_karma:
            return fail_result
    if condition.comment_karma is not None:
        if user.comment_karma < condition.comment_karma:
            return fail_result
    if condition.combined_karma is not None:
        if (user.link_karma + user.comment_karma) \
                < condition.combined_karma:
            return fail_result

    # account age check
    if condition.account_age is not None:
        if (datetime.utcnow() \
                - datetime.utcfromtimestamp(user.created_utc)).days \
                < condition.account_age:
            return fail_result

    # user passed all checks
    return not fail_result


def user_has_rank(subreddit, user, rank):
    """Returns true if user has sufficient rank in the subreddit."""
    sr_name = subreddit.display_name.lower()

    # fetch mod/contrib lists if necessary
    if sr_name not in user_has_rank.moderator_cache:
        mod_list = set()
        for mod in subreddit.get_moderators():
            mod_list.add(mod.name)
        user_has_rank.moderator_cache[sr_name] = mod_list

        contrib_list = set()
        for contrib in subreddit.get_contributors():
            contrib_list.add(contrib.name)
        user_has_rank.contributor_cache[sr_name] = contrib_list

    if user.name in user_has_rank.moderator_cache[sr_name]:
        if rank == 'moderator' or rank == 'contributor':
            return True
    elif user.name in user_has_rank.contributor_cache[sr_name]:
        if rank == 'contributor':
            return True
    return False
user_has_rank.moderator_cache = dict()
user_has_rank.contributor_cache = dict()


def get_permalink(item):
    """Returns the permalink for the item."""
    if isinstance(item, reddit.objects.Submission):
        return item.permalink
    elif isinstance(item, reddit.objects.Comment):
        return ('http://www.reddit.com/r/'+
                item.subreddit.display_name+
                '/comments/'+item.link_id.split('_')[1]+
                '/a/'+item.id)


def respond_to_modmail(modmail, start_time):
    """Responds to modmail if any submitters sent one before approval."""
    cache = list()
    # respond to any modmail sent in the last 5 mins
    time_window = timedelta(minutes=5)
    approvals = ActionLog.query.filter(
                    and_(ActionLog.action == 'approve',
                         ActionLog.action_time >= start_time)).all()

    for item in approvals:
        found = None
        done = False

        for i in cache:
            if datetime.utcfromtimestamp(i.created_utc) < item.created_utc:
                done = True
                break
            if (i.dest.lower() == '#'+item.subreddit.name.lower() and
                    i.author.name == item.user and
                    not i.replies):
                found = i
                break

        if not found and not done:
            for i in modmail:
                cache.append(i)
                if datetime.utcfromtimestamp(i.created_utc) < item.created_utc:
                    break
                if (i.dest.lower() == '#'+item.subreddit.name.lower() and
                        i.author.name == item.user and
                        not i.replies):
                    found = i
                    break

        if found:
            found.reply('Your submission has been approved automatically by '+
                cfg_file.get('reddit', 'username')+'. For future submissions '
                'please wait at least 5 minutes before messaging the mods, '
                'this post would have been approved automatically even '
                'without you sending this message.')


def get_meme_name(item):
    """Gets the item's meme name, if relevant/possible."""
    # determine the URL of the page that will contain the meme name
    if item.domain in ['quickmeme.com', 'qkme.me']:
        url = item.url
    elif item.domain.endswith('.qkme.me'):
        matches = re.search('.+/(.+?)\.jpg$', item.url)
        url = 'http://qkme.me/'+matches.group(1)
    elif item.domain.endswith('memegenerator.net'):
        for regex in ['/instance/(\\d+)$', '(\\d+)\.jpg$']:
            matches = re.search(regex, item.url)
            if matches:
                url = 'http://memegenerator.net/instance/'+matches.group(1)
                break
    elif item.domain == 'troll.me':
        url = item.url
    else:
        return None

    # load the page and extract the meme name
    try:
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page)

        if (item.domain in ['quickmeme.com', 'qkme.me'] or
                item.domain.endswith('.qkme.me')):
            return soup.findAll(id='meme_name')[0].text
        elif item.domain.endswith('memegenerator.net'):
            result = soup.findAll(attrs={'class': 'rank'})[0]
            matches = re.search('#\\d+ (.+)$', result.text)
            return matches.group(1)
        elif item.domain == 'troll.me':
            matches = re.search('^.+?\| (.+?) \|.+?$', soup.title.text)
            return matches.group(1)
    except:
        pass
    return None


# def most_similar_image(item):
#     """Gets the most similar comparison image to the item, if possible."""
#     comparison_path = 'comparison_images/'
# 
#     # convert common hosts to image address
#     if item.domain == 'imgur.com':
#         matches = re.search('imgur\.com/(.+)$', item.url)
#         url = 'http://i.imgur.com/'+matches.group(1)+'.jpg'
#     else:
#         url = item.url
# 
#     # return if we don't have an image url at this point
#     if not (url.endswith('.jpg') or url.endswith('.png')):
#         return None
# 
#     try:
#         # get the image and load into PIL
#         image_file = urllib2.urlopen(url)
#         image_stream = StringIO(image_file.read())
#         submitted_image = Image.open(image_stream)
# 
#         # compare against all the images in the comparison_images dir
#         best_similarity = 0
#         best_match = None
#         comparison_files = os.listdir(comparison_path)
#         for comparison_file in comparison_files:
#             comparison_image = Image.open(comparison_path+comparison_file)
#             comparer = FuzzyImageCompare(submitted_image, comparison_image)
#             similarity = comparer.similarity()
#             logging.debug('      Similarity to %s = %s', comparison_file, similarity)
#             if similarity > best_similarity:
#                 best_similarity = similarity
#                 best_match = comparison_file
# 
#         # if the similarity is high enough, return image name, else nothing
#         if best_similarity >= MIN_IMAGE_SIMILARITY:
#             return os.path.splitext(best_match)[0]
#         else:
#             return None
#     except:
#         return None


def elapsed_since(start_time):
    """Returns a timedelta for how much time has passed since start_time."""
    elapsed = time() - start_time
    return timedelta(seconds=round(elapsed))


def condition_complexity(condition):
    """Returns a value representing how difficult a condition is to check."""
    complexity = 0

    # approving or removing requires a request
    if condition.action in ('approve', 'remove'):
        complexity += 1

    # meme_name requires a (heavy) external site page load
    if condition.attribute == 'meme_name':
        complexity += 10

    # image similarity requires downloading an image + comparing
    if condition.attribute == 'similar_image':
        complexity += 100

    # checking user requires a page load
    if (condition.is_gold is not None or
            condition.is_shadowbanned is not None or
            condition.link_karma is not None or
            condition.comment_karma is not None or
            condition.combined_karma is not None or
            condition.account_age is not None):
        complexity += 1

    # checking shadowbanned requires an extra page load
    if condition.is_shadowbanned is not None:
        complexity += 1

    if condition.comment is not None:
        # commenting+distinguishing requires 2 requests
        if condition.comment_method == 'comment':
            complexity += 2
        else:
            complexity += 1

    # add complexities of all sub-conditions too
    for sub in condition.additional_conditions:
        complexity += condition_complexity(sub)

    return complexity


def main():
    logging.config.fileConfig(path_to_cfg)
    start_utc = datetime.utcnow()
    start_time = time()

    global r
    try:
        r = reddit.Reddit(user_agent=cfg_file.get('reddit', 'user_agent'))
        logging.info('Logging in as %s', cfg_file.get('reddit', 'username'))
        r.login(cfg_file.get('reddit', 'username'),
            cfg_file.get('reddit', 'password'))

        subreddits = Subreddit.query.filter(Subreddit.enabled == True).all()
        sr_dict = dict()
        for subreddit in subreddits:
            sr_dict[subreddit.name.lower()] = subreddit
        mod_subreddit = r.get_subreddit('mod')
    except Exception as e:
        logging.error('  ERROR: %s', e)

    # check reports
    items = mod_subreddit.get_reports(limit=1000)
    stop_time = datetime.utcnow() - REPORT_BACKLOG_LIMIT
    check_items('report', items, sr_dict, stop_time)

    # check spam
    items = mod_subreddit.get_modqueue(limit=1000)
    stop_time = (db.session.query(func.max(Subreddit.last_spam))
                 .filter(Subreddit.enabled == True).one()[0])
    check_items('spam', items, sr_dict, stop_time)

    # check new submissions
    items = mod_subreddit.get_new_by_date(limit=1000)
    stop_time = (db.session.query(func.max(Subreddit.last_submission))
                 .filter(Subreddit.enabled == True).one()[0])
    check_items('submission', items, sr_dict, stop_time)

    # check new comments
    comment_multi = '+'.join([s.name for s in subreddits
                              if not s.reported_comments_only])
    if comment_multi:
        comment_multi_sr = r.get_subreddit(comment_multi)
        items = comment_multi_sr.get_comments(limit=1000)
        stop_time = (db.session.query(func.max(Subreddit.last_comment))
                     .filter(Subreddit.enabled == True).one()[0])
        check_items('comment', items, sr_dict, stop_time)

    # respond to modmail
    try:
        respond_to_modmail(r.user.get_modmail(), start_utc)
    except Exception as e:
        logging.error('  ERROR: %s', e)

    logging.info('Completed full run in %s', elapsed_since(start_time))


if __name__ == '__main__':
    main()
