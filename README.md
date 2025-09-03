# bandcamp-rss-feeds
A repo that generates personalized RSS feeds pointing to Bandcamp featuring aggregated updates on releases from those you are following, Wishlist updates, and Collection updates (purchases) with a reach goal of following updates, all compounded daily into 1 RSS feed with a summary of daily updates.

# Setup
This generator looks at bandcamp users listed in the `users.ssf`, with the following format:

```
{username} {fan_id}
```

Where username is the user name of the user according to the url of your profile's homepage: `https://bandcamp.com/username`(the former example's username is "username"). The `fan_id` can be found by examining the network requests bandcamp sends when loading pages. First, load your collection (via the normal `https://bandcamp.com/username`) and press the F12 key to open the dev tools in your browser. Navigate to the network tab in your browser, then refresh the page. Look for a request called `collection_summary`, click on it, then navigate to the `Preview` tab for this request. You should see something like the following in that tab:

```json
{
  "fan_id": 827391,
  "collection_summary": {
    "fan_id": 827391,
    "username": "username",
    "url": "https://bandcamp.com/username",
    ...
  }
}
```
The `"fan_id"` property is the ID that you need for the `users.ssf` file.

Once you have these values in the `user.ssf` file, the `user_orchestrator.py` file will run daily via the GitHub action. All updates from runs are found in the `rss` branch and not on the `main` branch, but the action itself can be found on the `main` branch. Note that if you fork this repo, you will need to create your own `rss` branch, at which point the action should automatically run to update that branch. The final rss file can be viewed at `bandcamp-rss-feeds/rss/final.rss`. It's recommended that you use the "raw" version of the RSS file, dependent on how your RSS reader of choice works. For Discord, I've used [MonitoRSS](https://github.com/synzen/monitorss). You can specify multiple users (one per-line) in the `user.ssf` file if you want to recieve updates for multiple users (this repo currently has 2 listed).

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
-  Bandcamp Friday Notifications [:no_entry: Currently not working]
   - User-independent and based on the official https://isitbandcampfriday.com/ website
