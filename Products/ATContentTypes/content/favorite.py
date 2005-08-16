#  ATContentTypes http://sf.net/projects/collective/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2005 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""


"""
__author__  = 'Christian Heimes <ch@comlounge.net>'
__docformat__ = 'restructuredtext'
__old_name__ = 'Products.ATContentTypes.types.ATFavorite'

import urlparse
import logging

from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from ComputedAttribute import ComputedAttribute
from ZODB.POSException import ConflictError

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent

from Products.Archetypes.public import Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget

from Products.ATContentTypes.config import PROJECTNAME
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.interfaces import IATFavorite
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

LOG = logging.getLogger('ATCT')

ATFavoriteSchema = ATContentTypeSchema.copy() + Schema((
    StringField('remoteUrl',
                required=True,
                searchable=True,
                accessor='_getRemoteUrl',
                primary=True,
                validators = (),
                widget = StringWidget(
                        description=("Add http:// to link outside the portal."),
                        description_msgid = "help_url",
                        label = "URL",
                        label_msgid = "label_url",
                        i18n_domain = "plone")),
    ))
finalizeATCTSchema(ATFavoriteSchema, moveDiscussion=False)

class ATFavorite(ATCTContent):
    """A placeholder item linking to a favorite object in the portal."""

    schema         =  ATFavoriteSchema

    content_icon   = 'favorite_icon.gif'
    meta_type      = 'ATFavorite'
    portal_type    = 'Favorite'
    archetype_name = 'Favorite'
    default_view   = 'favorite_view'
    immediate_view = 'favorite_view'
    suppl_views    = ()
    include_default_actions = False
    global_allow   = True
    filter_content_types  = True
    allowed_content_types = ()
    _atct_newTypeFor = {'portal_type' : 'CMF Favorite', 'meta_type' : 'Favorite'}
    typeDescription = 'A placeholder item linking to a favorite object in the portal.'
    typeDescMsgId  = 'description_edit_favorite'
    assocMimetypes = ()
    assocFileExt   = ('fav', )
    cmf_edit_kws   = ('remote_url',)

    __implements__ = ATCTContent.__implements__, IATFavorite

    security       = ClassSecurityInfo()

    # Support for preexisting api
    security.declareProtected(View, 'getRemoteUrl')
    def getRemoteUrl(self):
        """returns the remote URL of the Link
        """
        # need to check why this is different than PortalLink
        utool  = getToolByName(self, 'portal_url')
        portal_url = utool()
        remote = self._getRemoteUrl()
        if remote:
            if remote.startswith('/'):
                remote = remote[1:]
            return '%s/%s' % (portal_url, remote)
        else:
            return portal_url

    def _getRemoteUrl(self):
        """Accessor
        """
        return self.getField('remoteUrl').get(self)

    remote_url = ComputedAttribute(_getRemoteUrl, 1)

    security.declareProtected(ModifyPortalContent, 'setRemoteUrl')
    def setRemoteUrl(self, remote_url):
        """Set url relative to portal root
        """
        utool  = getToolByName(self, 'portal_url')
        # strip off scheme and machine from URL if present
        tokens = urlparse.urlparse(remote_url, 'http')
        if tokens[1]:
            # There is a nethost, remove it
            t=('', '') + tokens[2:]
            remote_url = urlparse.urlunparse(t)
        # if URL begins with site URL, remove site URL
        portal_url = utool.getPortalPath()
        i = remote_url.find(portal_url)
        if i==0:
            remote_url=remote_url[len(portal_url):]
        # if site is still absolute, make it relative
        if remote_url[:1]=='/':
            remote_url=remote_url[1:]

        self.getField('remoteUrl').set(self, remote_url)

    security.declareProtected(View, 'getIcon')
    def getIcon(self, relative_to_portal=0):
        """Instead of a static icon, like for Link objects, we want
        to display an icon based on what the Favorite links to.
        """
        obj =  self.getObject()
        if obj is not None:
            return obj.getIcon(relative_to_portal)
        else:
            return 'favorite_broken_icon.gif'

    security.declareProtected(View, 'getObject')
    def getObject(self):
        """Return the actual object that the Favorite is
        linking to
        """
        utool  = getToolByName(self, 'portal_url')
        portal = utool.getPortalObject()
        relative_url = self._getRemoteUrl()
        try:
            obj = portal.restrictedTraverse(relative_url)
        except ConflictError:
            raise
        except (KeyError, AttributeError, Unauthorized, 'Unauthorized', ):
            LOG.error('Failed to get object for %s with url of %s' % (repr(self),
                      relative_url), exc_info=True)
            obj = None
        return obj

    security.declarePrivate('cmf_edit')
    def cmf_edit(self, remote_url=None, **kwargs):
        self.update(remoteUrl = remote_url, **kwargs)

registerATCT(ATFavorite, PROJECTNAME)
