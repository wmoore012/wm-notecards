# Target analysis contract

Target analysis is both EDA and documentation. A model story cannot begin until the
reader knows exactly what the outcome means and what decision it may support.

## Target contract

Before target relationships or modeling, document:

- target field and plain-English definition;
- row grain and prediction/measurement window;
- valid domain and missing count;
- numerator, denominator, prevalence or distribution;
- why this outcome matches the analytical question;
- the business decision the score may inform;
- false-positive and false-negative consequences, including customer goodwill,
  capacity, privacy, and fairness;
- plausible relationships to inspect, labeled as hypotheses rather than truths;
- post-outcome fields and leakage risks.

Make a consequential target proportion visually loud with a big-number or pictogram
card. Keep its numerator and denominator visible.

## Choosing the model family

Use binary classification when the observed outcome is truly binary. Use regression
for a continuous outcome, count models for counts when appropriate, and survival or
time-to-event methods when timing and censoring are the question. Do not turn a useful
continuous measure into green/black merely to avoid a threshold decision.

A classification probability ranks cases. The operational threshold is a separate
business policy. Explain both.

## Relationships and unusual values

A binary target does not have box-plot outliers. Points beyond the whiskers belong to
the predictor distribution within a target group. Explain what that means, show group
sizes, and note that overlap weakens any one-field conclusion. Association is not
causation and does not automatically earn the field a place in the model.

## Classification evidence spine

For a public classification lesson:

1. Show target prevalence and the random-ranking PR baseline.
2. Split train, validation, and test explicitly. Validation chooses the model and
   threshold; test is opened once after those choices are fixed.
3. Pair the model score table with PR evidence. Do not rely on accuracy or ROC alone
   when the positive outcome is uncommon.
4. Use scikit-learn or another named, standard metrics implementation. Do not hand-roll
   common metrics unless the lesson is explicitly deriving them and tests compare the
   result with the library implementation.
5. Introduce threshold selection with the decision it changes. Pair exact false-positive
   and false-negative counts with the tradeoff visual. If F1 is used as a teaching rule,
   label it as a validation-derived balance, not a business policy.
6. Pair confusion counts with a confusion-matrix visual and translate both error types
   into the business consequence.
7. Teach signed coefficients or feature effects before interpreting them. Preserve the
   non-causal boundary.

Threshold choice belongs to the human. Surface contact capacity, intervention cost,
missed-opportunity cost, customer goodwill, fairness, and calibration before recommending
deployment.
