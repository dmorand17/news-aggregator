Ask the user the following questions one at a time, waiting for their answer before proceeding:

1. **Category** — which category should this feed be added to? List the existing categories from `config/feeds.yaml` as options, and offer "New category" as a choice.
2. **Name** — what display name should be used for this feed source?
3. **RSS URL** — what is the RSS/Atom feed URL?

If the user chose "New category", ask them for the new category name.

Once you have all three answers:
- Read `config/feeds.yaml`
- Add the new feed under the correct category (create the category if new)
- Write the updated `config/feeds.yaml`

Use the simple string format `"Name": "url"` unless the user specifies a filter keyword, in which case use the expanded format:
```yaml
"Name":
  url: "url"
  filter: "keyword"
```

After saving, confirm to the user what was added.
