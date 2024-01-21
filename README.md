# bandcamp-rss-feeds
Personalized and hand-built RSS feeds pointing to Bandcamp featuring aggregated updates on releases from those you are following, Wishlist updates, and Collection updates (purchases) with a reach goal of following updates, all compounded daily into 1 RSS feed with a summary of daily updates.

# Features

## Wishlist Updates
This tool supports updates from a user's wishlist page. If a user adds a release to their wishlist, it will appear in the aggregate message for that user when this rss feed updates. It is designed to track new wishlist items and assumes that the user usually does not un-wishlist items

### Limitations
- Limited to 20 new wishlist items per aggregate message
- Does not track "un-wishlisted" releases
- If you un-wishlist your most recent wishlisted release, the tool will output your twenty most recent wishlist items