# Static Files

The package to handler static files is
[bareASGI-static](https://github.com/rob-blackbourn/bareasgi-static).

## Installation

The package can be installed as follows.

```bash
pip install bareasgi-static
```

## Usage

Use the helper method to add support.

```python
import os.path
import uvicorn
from bareasgi import Application
from bareasgi_static import add_static_file_provider

here = os.path.abspath(os.path.dirname(__file__))

app = Application()
add_static_file_provider(app, os.path.join(here, simple_www))

uvicorn.run(app, port=9010)
```
