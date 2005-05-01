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
""" Topic:

"""

__author__  = 'Alec Mitchell'
__docformat__ = 'restructuredtext'
__old_name__ = 'Products.ATContentTypes.types.criteria.ATReferenceCriterion'

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.criteria import registerCriterion
from Products.ATContentTypes.criteria import LIST_INDICES
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.criteria.selection import ATSelectionCriterion

ATReferenceCriterionSchema = ATSelectionCriterion.schema

class ATReferenceCriterion(ATSelectionCriterion):
    """A reference criterion"""

    __implements__ = ATSelectionCriterion.__implements__ + (IATTopicSearchCriterion, )
    security       = ClassSecurityInfo()
    meta_type      = 'ATReferenceCriterion'
    archetype_name = 'Reference Criterion'
    typeDescription= ''
    typeDescMsgId  = ''

    shortDesc      = 'reference field select list'


    def getCurrentValues(self):
        catalog = getToolByName(self, 'portal_catalog')
        uid_cat = getToolByName(self, 'uid_catalog')
        options = catalog.uniqueValuesFor(self.Field())

        brains = uid_cat(UID=options, sort_on='Title')
        display_list = DisplayList([(b.UID, b.Title or b.id) for b in brains])

        return display_list

registerCriterion(ATReferenceCriterion, LIST_INDICES)