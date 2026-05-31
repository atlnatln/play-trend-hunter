/**
 * Node.js wrapper around google-play-scraper.
 * Outputs JSON to stdout for Python consumption.
 * Usage: node gplay_fetch.js <method> [args_json]
 */
const gplay = require('google-play-scraper').default;

const METHODS = {
  list: async (args) => {
    const { collection, category, num = 100, fullDetail = false } = args;
    return gplay.list({
      collection: gplay.collection[collection],
      category: gplay.category[category],
      num: Math.min(num, 100),
      fullDetail,
    });
  },
  app: async (args) => {
    const { appId, lang = 'en', country = 'us' } = args;
    return gplay.app({ appId, lang, country });
  },
  search: async (args) => {
    const { term, num = 30, lang = 'en', country = 'us' } = args;
    return gplay.search({ term, num: Math.min(num, 100), lang, country });
  },
  reviews: async (args) => {
    const { appId, num = 100, sort = 'NEWEST', lang = 'en', country = 'us' } = args;
    const sortMap = { NEWEST: gplay.sort.NEWEST, RATING: gplay.sort.RATING, HELPFULNESS: gplay.sort.HELPFULNESS };
    return gplay.reviews({ appId, num: Math.min(num, 200), sort: sortMap[sort] || gplay.sort.NEWEST, lang, country });
  },
  categories: async () => {
    const cats = await gplay.categories();
    return cats.map(c => ({ id: c }));
  },
};

async function main() {
  const method = process.argv[2];
  const args = process.argv[3] ? JSON.parse(process.argv[3]) : {};
  
  if (!METHODS[method]) {
    console.error(JSON.stringify({ error: `Unknown method: ${method}. Available: ${Object.keys(METHODS).join(', ')}` }));
    process.exit(1);
  }
  
  try {
    const result = await METHODS[method](args);
    const out = JSON.stringify(result, null, 0);
    if (!out) {
      console.error(JSON.stringify({ error: "Empty output from scraper" }));
      process.exit(1);
    }
    console.log(out);
  } catch (err) {
    console.error(JSON.stringify({ error: err.message }));
    process.exit(1);
  }
}

main();
