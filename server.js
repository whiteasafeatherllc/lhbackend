import express from "express";
import fetch from "node-fetch";
import cors from "cors";
import dotenv from "dotenv";
import snoowrap from "snoowrap";
import { TwitterApi } from "twitter-api-v2";

dotenv.config();
const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 5000;

// --- Reddit Setup ---
const reddit = new snoowrap({
  userAgent: process.env.REDDIT_USER_AGENT,
  clientId: process.env.REDDIT_CLIENT_ID,
  clientSecret: process.env.REDDIT_CLIENT_SECRET,
  refreshToken: null,
});

// --- Twitter Setup ---
const twitterClient = new TwitterApi({
  appKey: process.env.TWITTER_API_KEY,
  appSecret: process.env.TWITTER_API_SECRET,
  accessToken: process.env.TWITTER_ACCESS_TOKEN,
  accessSecret: process.env.TWITTER_ACCESS_SECRET,
});

// === Search ===
app.get("/search", async (req, res) => {
  const { keyword, platforms, page = 1, per_page = 10 } = req.query;
  let results = [];

  if (!keyword || !platforms) {
    return res.status(400).json({ error: "Missing keyword or platforms" });
  }

  try {
    const platformsArr = platforms.split(",");

    // --- Reddit ---
    if (platformsArr.includes("reddit")) {
      const posts = await reddit.getSubreddit("all").search({
        query: keyword,
        limit: per_page,
      });
      results.push(
        ...posts.map((p) => ({
          platform: "reddit",
          title: p.title,
          url: `https://reddit.com${p.permalink}`,
          snippet: p.selftext.substring(0, 200),
        }))
      );
    }

    // --- Google ---
    if (platformsArr.includes("google")) {
      const serp = await fetch(
        `https://serpapi.com/search.json?q=${encodeURIComponent(
          keyword
        )}&api_key=${process.env.SERPLY_API_KEY}`
      );
      const serpData = await serp.json();
      if (serpData.organic_results) {
        results.push(
          ...serpData.organic_results.slice(0, per_page).map((r) => ({
            platform: "google",
            title: r.title,
            url: r.link,
            snippet: r.snippet || "",
          }))
        );
      }
    }

    // --- Twitter ---
    if (platformsArr.includes("twitter")) {
      const tweets = await twitterClient.v2.search(keyword, {
        max_results: per_page,
      });
      if (tweets.data) {
        results.push(
          ...tweets.data.map((t) => ({
            platform: "twitter",
            title: t.text.substring(0, 100),
            url: `https://twitter.com/i/web/status/${t.id}`,
            snippet: t.text,
          }))
        );
      }
    }

    // --- News ---
    if (platformsArr.includes("news")) {
      const news = await fetch(
        `https://www.searchapi.io/api/v1/search?engine=news&api_key=${
          process.env.SEARCHAPI_IO_KEY
        }&q=${encodeURIComponent(keyword)}`
      );
      const newsData = await news.json();
      if (newsData.news_results) {
        results.push(
          ...newsData.news_results.slice(0, per_page).map((n) => ({
            platform: "news",
            title: n.title,
            url: n.link,
            snippet: n.snippet || "",
          }))
        );
      }
    }

    res.json({ results });
  } catch (err) {
    console.error("Search error:", err);
    res.status(500).json({ error: "Failed to fetch results" });
  }
});

// === Generate (AI messaging) ===
app.post("/generate_message", async (req, res) => {
  const { service, tone, location, context } = req.body;

  if (!service || !context) {
    return res.status(400).json({ error: "Missing required fields" });
  }

  // For now, generate a simple template message
  const message = `Hi, I noticed your post about "${context}". 
I specialize in ${service}${location ? " around " + location : ""}. 
Would love to connect and see how I can help.`;

  res.json({ message });
});

app.listen(PORT, () => console.log(`✅ Backend running on port ${PORT}`));
