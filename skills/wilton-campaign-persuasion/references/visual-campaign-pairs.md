# Visual campaign pairs

Use this reference for screenshot sequences and notebook comparison campaigns.

## Governing comparison contract

Keep the analytical work identical on both sides:

- same synthetic source rows;
- same feature names;
- same train/validation split;
- same preprocessing fit scope;
- same fitted model;
- same metric values;
- same examples.

Compare communication, not scientific competence.

The source receipt must be real. Build it as an executable `.ipynb` with native
Markdown cells and native Pandas outputs. Put the matching notecard in the next
notebook cell and export HTML from that executed notebook. Never imitate Markdown,
Pandas, or Jupyter with screenshot-only HTML panels; an attentive reader can feel the
difference, and a squeezed mock table distorts the very problem being demonstrated.

The `.ipynb` is canonical. HTML is a review and sharing export, not a separately
maintained story.

## One receipt per group

Each group must fit a clean screenshot and answer one question. Show the conventional
notebook artifact first, then the corresponding notecard sequence. Do not place the
entire project in one enormous side-by-side.

Useful groups:

1. raw rows beside field-role and dtype review;
2. `df.describe()` beside numeric micro-profiles;
3. missing counts beside candidate methods and the applied decision log;
4. category counts beside a ranked table with stable preattentive grouping;
5. ordinary Markdown question beside a question card paired with evidence;
6. ordinary Markdown caution beside a counterintuitive boundary card;
7. ordinary Markdown instructions beside an explicit reading-order card;
8. raw model scores beside a styled validation comparison;
9. printed classification report beside threshold/confusion evidence;
10. coefficient dump beside a bounded plain-English interpretation;
11. end-of-notebook Markdown summary beside an evidence-backed takeaway and human decision.

## Attribute density

Use a compact source table when the lesson is one row, one category, or one metric. Use
a wide source table when cognitive overload itself is the receipt. Never label either
artifact “simple,” “40 columns,” “low attribute,” or “high attribute” inside the visual.

## Screenshot language

Headings belong to the analysis, not the production process. Prefer:

- “Can we predict which customer will leave?”
- “Which fields arrived ready to model?”
- “What did the training split decide to fill?”
- “Which model survives validation?”
- “What changes when recall matters more?”

Avoid:

- “Before vs. after”
- “Traditional pandas workflow”
- “The better version”
- “What this component does”
- “How the UI helps”
- “Screenshot 3”

The surrounding post can name the comparison. The notebook should remain believable as
a real logistic-regression analysis.

## Markdown comparisons

Do not sabotage the Markdown side with bad writing. Give it the strongest ordinary
version a thoughtful student would write. Then let the notecard side demonstrate what
the framework adds: stable role, visual hierarchy, evidence adjacency, conclusion
boundary, and an explicit human decision.

## Campaign rhythm

Sequence screenshots as:

`human cost → receipt → contradiction → product response → evidence → decision`

The post can say less because the notebook proves the point.
