# Jinja2 Templating

The package that provides
[jinja2](https://jinja.palletsprojects.com/en/2.10.x/)
support is [bareASGI-jinja2](https://github.com/rob-blackbourn/bareasgi-jinja2).

## Installation

The package can be installed as follows.

```bash
pip install bareasgi-jinja2
```

## Usage

A helper method can be used to add the support.
Assuming the templates are in a folder named `templates`:

```python
from bareasgi import Application,
import bareasgi_jinja2
import jinja2
import pkg_resources

app = Application(info=dict(config=config))

templates = pkg_resources.resource_filename(__name__, "templates")
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(templates),
    autoescape=jinja2.select_autoescape(['html', 'xml']),
    enable_async=True
)
bareasgi_jinja2.add_jinja2(app, env)
```

A class method `apply` on the `Jinja2TemplateProvider` can be used to handle the
request.

```python
from bareasgi_jinja2 import Jinja2TemplateProvider

async def handle_index_request(request):
    return await Jinja2TemplateProvider.apply(
        request,
        'index.html',
        {'title': 'bareASGI'}
    )
```

The method specifies the template to be used and a `dict` of values which are
available in the template.
