# bandcamp-rss-feeds
Personalized and hand-built RSS feeds pointing to Bandcamp featuring aggregated updates on releases from those you are following, Wishlist updates, and Collection updates (purchases) with a reach goal of following updates, all compounded daily into 1 RSS feed with a summary of daily updates.

# Features
This tool creates an RSS feed for the following "actions" that can occur related to a users bandcamp account, scheduled daily through a github action.
- Wishlist Updates (from https://bandcamp.com/{user}/wishlist)
  - Limited to 20 new wishlist items per aggregate message
  - Does not track "un-wishlisted" releases
- Following Updates (from https://bandcamp.com/{user}/following/artists_and_labels)
  - Limited to 45 new artists a user is following
  - Does not track "un-followed" artists
- Collection Updates (from https://bandcamp.com/{user})
  - Limited to 20 new purchases