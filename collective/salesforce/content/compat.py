try:
	from zope.component.hooks import getSite
except ImportError:
	from zope.app.component.hooks import getSite

try:
	from zope.container.interfaces import INameChooser
except ImportError:
	from zope.app.container.interfaces import INameChooser
