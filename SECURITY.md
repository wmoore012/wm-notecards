# Security policy

Please report suspected vulnerabilities privately through GitHub's security advisory
flow rather than a public issue.

Notebook exports can accidentally contain secrets, local paths, customer data,
execution outputs, or embedded source. Before sharing an `.ipynb`, HTML file, image,
or Colab bundle:

- clear outputs and execution counts unless the outputs are intentionally public;
- scan source and metadata for credentials and local paths;
- verify that embedded files are intended for redistribution;
- use synthetic or explicitly licensed data in examples;
- never include `.env` files or browser-testing artifacts.

Supported security fixes target the latest released version.
