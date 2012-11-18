--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

--
-- Name: conditions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pornoverlord
--

SELECT pg_catalog.setval('conditions_id_seq', 16, true);


--
-- Name: subreddits_subreddit_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pornoverlord
--

SELECT pg_catalog.setval('subreddits_subreddit_id_seq', 47, true);


--
-- Data for Name: subreddits; Type: TABLE DATA; Schema: public; Owner: pornoverlord
--

COPY subreddits (id, name, enabled, last_submission, last_spam, auto_reapprove, check_all_conditions, last_comment, reported_comments_only) FROM stdin;
20	BotanicalPorn	t	2012-11-18 20:16:39	2012-11-13 23:32:05	f	t	1900-01-01 00:00:00	t
21	AlbumArtPorn	t	2012-11-18 21:52:03	2012-11-18 02:24:52	f	t	1900-01-01 00:00:00	t
28	ClimbingPorn	t	2012-11-17 08:25:07	2012-11-15 11:41:31	f	t	1900-01-01 00:00:00	t
32	CarPorn	t	2012-11-18 22:14:07	2012-11-18 10:35:41	f	t	1900-01-01 00:00:00	t
4	VillagePorn	t	2012-11-18 22:17:43	2012-11-17 23:43:34	f	t	1900-01-01 00:00:00	t
31	CemeteryPorn	t	2012-11-18 20:45:09	2012-11-12 03:52:30	f	t	1900-01-01 00:00:00	t
34	FractalPorn	t	2012-11-18 05:42:31	2012-11-16 23:31:38	f	t	2012-02-28 02:02:33	t
41	AgriculturePorn	t	2012-11-18 05:45:34	2012-11-17 09:51:41	f	t	2012-06-24 02:25:38	t
13	GeekPorn	t	2012-11-17 20:18:31	2012-11-12 22:15:13	f	t	1900-01-01 00:00:00	t
26	InfrastructurePorn	t	2012-11-17 22:17:03	2012-11-15 11:22:19	f	t	1900-01-01 00:00:00	t
6	HistoryPorn	t	2012-11-18 22:27:22	2012-11-18 13:51:39	f	t	1900-01-01 00:00:00	t
7	MapPorn	t	2012-11-18 22:29:37	2012-11-18 20:53:24	f	t	1900-01-01 00:00:00	t
22	MoviePosterPorn	t	2012-11-18 16:20:12	2012-11-18 12:56:20	f	t	1900-01-01 00:00:00	t
18	AdrenalinePorn	t	2012-11-18 22:36:08	2012-11-17 17:10:56	f	t	1900-01-01 00:00:00	t
47	F1Porn	t	2012-10-18 22:44:33	2012-10-18 22:44:33	f	t	1900-01-01 00:00:00	t
17	DesignPorn	t	2012-11-18 19:13:36	2012-11-16 20:36:02	f	t	1900-01-01 00:00:00	t
35	ArtPorn	t	2012-11-18 19:14:43	2012-11-15 16:02:38	f	t	2012-03-25 18:24:11	t
43	FuturePorn	t	2012-11-18 19:12:23	2012-11-13 10:36:35	f	t	2012-07-17 18:29:15	t
15	AnimalPorn	t	2012-11-18 22:45:38	2012-11-18 01:15:42	f	t	1900-01-01 00:00:00	t
24	SkyPorn	t	2012-11-18 22:58:10	2012-11-17 17:21:37	f	t	1900-01-01 00:00:00	t
5	RoomPorn	t	2012-11-18 17:13:31	2012-11-17 13:10:43	f	t	1900-01-01 00:00:00	t
42	GeologyPorn	t	2012-11-17 02:07:39	2012-10-17 20:25:53	f	t	2012-07-05 19:14:43	t
2	EarthPorn	t	2012-11-18 23:03:25	2012-11-18 21:31:39	f	t	1900-01-01 00:00:00	t
33	ArchitecturePorn	t	2012-11-18 19:16:05	2012-11-17 18:34:22	f	t	1900-01-01 00:00:00	t
37	GunPorn	t	2012-11-18 17:18:34	2012-11-16 03:23:17	f	t	2012-04-20 12:57:56	t
10	HumanPorn	t	2012-11-18 23:05:09	2012-11-15 03:11:16	f	t	1900-01-01 00:00:00	t
29	MacroPorn	t	2012-11-18 21:27:46	2012-11-15 04:30:44	f	t	1900-01-01 00:00:00	t
30	InstrumentPorn	t	2012-11-18 19:23:23	2012-11-18 01:34:07	f	t	1900-01-01 00:00:00	t
39	DessertPorn	t	2012-11-18 00:27:10	2012-11-17 21:54:03	f	t	2012-06-12 17:06:04	t
14	DestructionPorn	t	2012-11-18 23:05:08	2012-11-18 22:55:02	f	t	1900-01-01 00:00:00	t
40	BoatPorn	t	2012-11-18 23:01:56	2012-11-15 14:19:46	f	t	1900-01-01 00:00:00	t
3	SpacePorn	t	2012-11-18 23:09:00	2012-11-18 05:56:25	f	t	1900-01-01 00:00:00	t
23	MilitaryPorn	t	2012-11-18 23:09:41	2012-11-18 15:00:36	f	t	1900-01-01 00:00:00	t
46	FoodPorn	t	2012-11-18 23:06:13	2012-11-18 21:49:12	f	t	1900-01-01 00:00:00	t
38	CulinaryPorn	t	2012-11-18 17:27:10	2012-11-01 13:05:04	f	t	2012-06-12 17:06:04	t
44	WinterPorn	t	2012-11-17 17:49:20	2012-11-18 11:44:14	f	t	1900-01-01 00:00:00	t
1	CityPorn	t	2012-11-18 21:44:59	2012-11-18 13:19:50	f	t	1900-01-01 00:00:00	t
11	WaterPorn	t	2012-11-18 17:36:37	2012-11-13 09:08:41	f	t	1900-01-01 00:00:00	t
36	ExposurePorn	t	2012-11-18 15:14:39	2012-11-18 11:25:42	f	t	2012-03-29 02:59:30	t
19	AdPorn	t	2012-11-18 11:53:23	2012-11-17 18:33:55	f	t	1900-01-01 00:00:00	t
8	AbandonedPorn	t	2012-11-18 21:44:27	2012-11-18 20:17:35	f	t	1900-01-01 00:00:00	t
9	QuotesPorn	t	2012-11-18 21:44:32	2012-11-17 18:32:00	f	t	1900-01-01 00:00:00	t
25	NewsPorn	t	2012-11-18 03:09:39	2012-11-13 06:47:57	f	t	1900-01-01 00:00:00	t
27	FirePorn	t	2012-11-18 15:30:58	2012-11-18 06:14:40	f	t	1900-01-01 00:00:00	t
16	BookPorn	t	2012-11-18 18:23:04	2012-11-07 14:25:52	f	t	1900-01-01 00:00:00	t
12	MachinePorn	t	2012-11-18 18:33:22	2012-11-18 02:34:58	f	t	1900-01-01 00:00:00	t
\.


--
-- Data for Name: conditions; Type: TABLE DATA; Schema: public; Owner: pornoverlord
--

COPY conditions (id, subreddit_id, subject, attribute, value, is_gold, account_age, link_karma, comment_karma, combined_karma, inverse, parent_id, action, short_reason, comment, notes, is_shadowbanned, spam, num_reports, auto_reapproving, comment_method, account_rank, set_flair_text, set_flair_class) FROM stdin;
10	3	submission	domain	.*hubblesite\\.org	\N	30	100	\N	\N	f	\N	approve	\N	\N	SpacePorn domain whitelist	f	\N	\N	f	\N	\N	\N	\N
9	\N	submission	domain	.*(deviantart\\..+|min\\.us|minus\\.com|wikimedia\\.org|500px\\.com|esa\\.int|nationalgeographic\\.com|googleusercontent\\.com|googleapis\\.com|pbase\\.com|smugmug\\.com|shadowness\\.com|summitpost\\.org|nato\\.int|\\.gov|eho\\.st)	\N	30	100	\N	\N	f	\N	approve	\N	\N	Network-wide domain whitelist	f	\N	\N	f	\N	\N	\N	\N
11	\N	submission	title	.*request.*	\N	\N	\N	\N	\N	t	7	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
7	\N	submission	domain	self\\.QuotesPorn	\N	\N	\N	\N	\N	t	1	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
8	\N	submission	title	.*\\[meta\\].*	\N	\N	\N	\N	\N	t	1	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
1	\N	submission	title	.*(?:(?:\\d\\d?[ ,\\.])?\\d\\d\\d)(?:\\s*px?)?\\s*(?:[x×\\* -]|by)\\s*(?:(?:\\d\\d?[ ,\\.])?\\d\\d\\d)(?:\\s*px?)?.*	\N	\N	\N	\N	\N	t	\N	remove	resolution	You did not include the image's resolution in the title. You should put the resolution in brackets at the end of your title.	\N	\N	f	\N	f	comment	\N	\N	\N
2	\N	submission	url	.*(imgur\\.com/a/).*	\N	\N	\N	\N	\N	f	\N	remove	collection	This is a collection, and we only allow single image submissions in this subreddit. If you would like to submit a collection, please pick your favorite image from the collection, and submit that instead. You can leave a link to the full collection as a comment.	\N	\N	f	\N	f	comment	\N	\N	\N
3	\N	submission	domain	.*(youtube\\.com|youtu\\.be|vimeo\\.com|liveleak\\.com|dailymotion\\.com|pinkbike\\.com).*	\N	\N	\N	\N	\N	f	\N	remove	inappropriate	Videos have been banned from the network. More information regarding this change can be found [here](http://www.reddit.com/r/PornOverlords/comments/nz6jx/videos_are_now_banned_from_the_network_the_vote/). In the meantime, you can probably submit it [here](http://www.reddit.com/r/VideoPorn), but pay attention to the rules in the sidebar. They are slightly different.	\N	\N	t	\N	f	comment	\N	\N	\N
12	\N	submission	domain	.*\\.xxx	\N	\N	\N	\N	\N	f	\N	remove	spam	This is spam	\N	\N	t	\N	f	comment	\N	\N	\N
5	\N	submission	domain	.*(quickmeme\\.com|qkme\\.me|memegenerator\\.net|diylol\\.com|troll\\.me|memebase\\.com|icanhascheezburger\\.com|cheezburger\\.com|9gag\\.com|livememe\\.com).*	\N	\N	\N	\N	\N	f	\N	remove	inappropriate	Image macros and memes are not allowed in the SFWPorn Network. /r/AdviceAnimals may be a more appropriate place to submit.	\N	\N	t	\N	f	comment	\N	\N	\N
6	\N	submission	domain	(bit\\.ly|normalurl\\.com|goo\\.gl|tinyurl\\.com|2ty\\.in|birurl\\.com|tiny\\.cc|migre\\.me|flic\\.kr|t\\.co)	\N	\N	\N	\N	\N	f	\N	remove	shortened	URL-shorteners are not allowed in the SFWPorn network. Please submit the direct link to the image (as long as it is the original source or one of the approved hosts in the FAQ).	\N	\N	t	\N	f	comment	\N	\N	\N
16	\N	submission	title	.*\\[(oc|os)\\].*	\N	\N	\N	\N	\N	f	\N	approve	\N	\N	Auto-approve [OC] and [OS] tags.	f	\N	\N	f	\N	\N	\N	\N
4	\N	submission	domain	.*(facebook|fbcdn|wallpaper|wallbase\\.cc|amazonaws\\.com|twitpic\\.com|twimg\\.com|imageshack\\.(us|com)|photobucket\\.com|tinypic\\.com).*	\N	\N	\N	\N	\N	f	\N	remove	source	The image is not hosted by an approved host.	\N	\N	t	\N	f	comment	\N	\N	\N
15	\N	submission	domain	.*(flickr\\.com)	\N	\N	\N	\N	\N	f	\N	approve	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N
13	\N	both	user	.*	\N	\N	\N	\N	\N	f	\N	remove	\N	\N	\N	t	t	\N	f	\N	\N	\N	\N
\.


--
-- PostgreSQL database dump complete
--

