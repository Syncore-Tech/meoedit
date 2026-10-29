-- Anonymous usage counts from the engine's /ping (one per installed version). No IP, no id.
CREATE TABLE IF NOT EXISTS pings (
  day TEXT NOT NULL,      -- UTC date, YYYY-MM-DD
  version TEXT NOT NULL,
  os TEXT NOT NULL,       -- mac | windows | linux | other
  cmd TEXT NOT NULL,      -- first command run with this version
  country TEXT NOT NULL,  -- from Cloudflare, XX if unknown
  n INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (day, version, os, cmd, country)
);
