# bandcamp-rss-feeds
A repo that generates personalized RSS feeds pointing to Bandcamp featuring releases from those you are following, wishlist updates, following updates and collection updates (purchases), all compounded daily into 1 RSS feed summary.

# Setup

First, fork the repo. Be sure to keep at least the `main` and the `rss` branches in your fork. Be sure to sync both branches in your fork when there is an update. It is highly likely that you will encounter merge conflicts when syncing the `rss` branch. As an alternative, you may merge any changes on `main` into your `rss` branch (this repo will keep those branches in sync behaviorally and your fork should also).

This generator looks at bandcamp users listed in the `users.ssf`, with the following format:

```
{username} {fan_id}
```

Where username is the user's slug according to the url of your profile's homepage: `https://bandcamp.com/username` (the former example's username is "username"). The `fan_id` is the internal ID that bandcamp assigns to each user. The `fan_id` is optional and this project will automatically find it for you and write it in the `users.ssf` file after the first run. You can specify multiple users (one per-line) in the `user.ssf` file if you want to recieve updates for multiple users (this repo currently has 2 listed).

Once you have at least the username value in the `users.ssf` file, the `user_orchestrator.py` file will run daily via the GitHub action. All updates from runs are found in the `rss` branch and not on the `main` branch, but the action yaml itself can be found on the `main` branch.

The final RSS file can be viewed at `bandcamp-rss-feeds/rss/final.rss`. It's recommended that you use the "raw" version of the RSS file, dependent on how your RSS reader of choice works. For Discord, I've used [MonitoRSS](https://github.com/synzen/monitorss).

# Features
This tool creates an RSS feed for the following "actions" that can occur related to a users bandcamp account, scheduled daily through a github action.
- Wishlist Updates (from https://bandcamp.com/{user}/wishlist)
  - Does not track "un-wishlisted" releases
- Following Updates (from https://bandcamp.com/{user}/following/artists_and_labels)
  - Does not track "un-followed" artists
- Collection Updates (from https://bandcamp.com/{user})
- Release Updates (from all artist hompages on bandcamp)
  - Only notifies for artists you follow
  - If you follow an artist, all releases on that day will not appear as new.
    - Any releases released after the day of following a new artist will appear
-  Bandcamp Friday Notifications [ :warning: Not consistently working]
   - User-independent and based on the official https://isitbandcampfriday.com/ website
