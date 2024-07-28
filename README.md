# bandcamp-rss-feeds
Personalized and hand-built RSS feeds pointing to Bandcamp featuring aggregated updates on releases from those you are following, Wishlist updates, and Collection updates (purchases) with a reach goal of following updates, all compounded daily into 1 RSS feed with a summary of daily updates.

# Setup
This generator looks at bandcamp users listed in the `users.ssf`, with the following format:

```
{username} {fan_id}
```

Where username is the user name of the user according to the url of your profile's homepage: `https://bandcamp.com/username`(the former example's username is "username"). The `fan_id` can be found by examining the network requests bandcamp sends when loading pages. First, load your collection (via the normal `https://bandcamp.com/username`) and press the F12 key to open the dev tools in your browser. Navigate to the network tab in your browser, then refresh the page. Look for a request called `collection_summary`, click on it, then navigate to the `Preview` tab for this request. You shouldl see something like the following in that tab:

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

Once you have these values in the `user.ssf` file, the `user_orchestrator.py` file will run daily via the GitHub action. All updates from runs are found in the `rss` branch, and not on the `main`, but the action itself can be found on the `main` branch.

# Features
This tool creates an RSS feed for the following "actions" that can occur related to a users bandcamp account, scheduled daily through a github action.
- Wishlist Updates (from https://bandcamp.com/{user}/wishlist)
  - Does not track "un-wishlisted" releases
- Following Updates (from https://bandcamp.com/{user}/following/artists_and_labels)
  - Does not track "un-followed" artists
- Collection Updates (from https://bandcamp.com/{user})
- Release Updates (from all artist hompages on bandcamp)
  - Atists that only have 1 track will not have the correct link displayed in the release updates, but the update will still appear
    - This would happen if you follow an artist with no releases, then that artist releases a track
-  Bandcamp Friday Notifications
   - User-independent and based on the official https://isitbandcampfriday.com/ website
