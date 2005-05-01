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

__author__ = 'Christian Heimes <ch@comlounge.net>'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))
from DateTime import DateTime

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase
from Missing import MV

from Products.CMFCore import CMFCorePermissions
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.public import *
import time

from Interface.Verify import verifyObject
from Products.Archetypes.interfaces.base import IBaseContent
from Products.Archetypes.interfaces.referenceable import IReferenceable
from Products.Archetypes.interfaces.metadata import IExtensibleMetadata

from Products.ATContentTypes.interfaces import IATTopicCriterion
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.interfaces import IATTopicSortCriterion

from Products.ATContentTypes.criteria.base import ATBaseCriterion
from Products.ATContentTypes.criteria.date import \
    ATDateCriteria 
from Products.ATContentTypes.criteria.list import \
    ATListCriterion
from Products.ATContentTypes.criteria.simpleint import \
    ATSimpleIntCriterion
from Products.ATContentTypes.criteria.simplestring import \
    ATSimpleStringCriterion
from Products.ATContentTypes.criteria.portaltype import \
    ATPortalTypeCriterion
from Products.ATContentTypes.criteria.sort import \
    ATSortCriterion
from Products.ATContentTypes.criteria.selection import \
    ATSelectionCriterion
from Products.ATContentTypes.criteria.daterange import \
    ATDateRangeCriterion
from Products.ATContentTypes.criteria.reference import \
    ATReferenceCriterion
from Products.ATContentTypes.criteria.boolean import \
    ATBooleanCriterion
from Products.ATContentTypes.criteria.portaltype import \
    ATPortalTypeCriterion
from Products.ATContentTypes.criteria.currentauthor import \
    ATCurrentAuthorCriterion
tests = []

class CriteriaTest(atcttestcase.ATCTSiteTestCase):

    klass = None
    portal_type = None
    title = None
    meta_type = None

    def afterSetUp(self):
        atcttestcase.ATCTSiteTestCase.afterSetUp(self)
        self.dummy = self.createDummy(self.klass)

    def createDummy(self, klass, id='dummy'):
        folder = self.folder
        if klass is not None:
            dummy = klass(id, 'dummyfield')
            # put dummy in context of portal
            folder._setObject(id, dummy)
            dummy = getattr(folder, id)
            dummy.initializeArchetype()
        else:
            dummy = None
        return dummy

    def test_000testsetup(self):
        if self.klass is not None:
            self.failUnless(self.klass)
            self.failUnless(self.portal_type)
            self.failUnless(self.title)
            self.failUnless(self.meta_type)
        
    def test_multipleCreateVariants(self):
        klass = self.klass
        id = 'dummy'
        field = 'dummyfield'
        if klass is not None:
            dummy = klass(id, field)
            self.failUnless(dummy.getId(), id)
            self.failUnless(dummy.Field(), field)

            dummy = klass(id=id, field=field)
            self.failUnless(dummy.getId(), id)
            self.failUnless(dummy.Field(), field)

            dummy = klass(field, oid=id)
            self.failUnless(dummy.getId(), id)
            self.failUnless(dummy.Field(), field)

            dummy = klass(field=field, oid=id)
            self.failUnless(dummy.getId(), id)
            self.failUnless(dummy.Field(), field)
    
    def test_typeInfo(self):
        if self.dummy is not None:
            ti = self.dummy.getTypeInfo()
            self.failUnlessEqual(ti.getId(), self.portal_type)
            self.failUnlessEqual(ti.Title(), self.title)
            self.failUnlessEqual(ti.Metatype(), self.meta_type)
        
    def test_implements(self):
        if self.dummy is not None:
            self.failIf(IReferenceable.isImplementedBy(self.dummy))
            self.failIf(IExtensibleMetadata.isImplementedBy(self.dummy))
            self.failIf(self.dummy.isReferenceable)
            self.failUnless(IBaseContent.isImplementedBy(self.dummy))
            self.failUnless(IATTopicCriterion.isImplementedBy(self.dummy))
            self.failUnless(verifyObject(IBaseContent, self.dummy))
            self.failUnless(verifyObject(IATTopicCriterion, self.dummy))
        

class TestATBaseCriterion(CriteriaTest):
    klass = ATBaseCriterion
    title = 'Base Criterion'
    meta_type = 'ATBaseCriterion'
    portal_type = 'ATBaseCriterion'

    def test_typeInfo(self):
        # not registered
        pass

tests.append(TestATBaseCriterion)


class TestATDateCriteria(CriteriaTest):
    klass = ATDateCriteria
    title = 'Friendly Date Criteria'
    meta_type = 'ATFriendlyDateCriteria'
    portal_type = 'ATDateCriteria'

    def test_LessThanPast(self):
        # A query of the form 'Less than 14 days ago' should generate a min:max
        # query with a start 14 days in the past and an end in the present
        self.dummy.field = 'created'
        self.dummy.setOperation('less')
        self.dummy.setDateRange('-')
        self.dummy.setValue('14')
        expected_begin = DateTime().earliestTime() - 14
        items = self.dummy.getCriteriaItems()
        self.assertEquals(len(items),1)
        query = items[0][1]
        field = items[0][0]
        self.assertEquals(field, 'created')
        #range should start in past at the beginning of the day
        self.assertEquals(query['query'][0], expected_begin)
        # range should end today
        self.assertEquals(query['query'][1].earliestTime(),
                                                    DateTime().earliestTime())
        self.assertEquals(query['range'], 'min:max')

    def test_LessThanFuture(self):
        # A query of the form 'Less than 14 days in the future' should generate
        # a min:max query with an end 14 days in the future and a start in the
        # present
        self.dummy.field = 'created'
        self.dummy.setOperation('less')
        self.dummy.setDateRange('+')
        self.dummy.setValue('14')
        expected_end = DateTime().latestTime() + 14
        items = self.dummy.getCriteriaItems()
        self.assertEquals(len(items),1)
        query = items[0][1]
        #Range should end on future date at the end of the day
        self.assertEquals(query['query'][1], expected_end)
        #Range should start today
        self.assertEquals(query['query'][0].earliestTime(),
                                                    DateTime().earliestTime())
        self.assertEquals(query['range'], 'min:max')

    def test_MoreThanPast(self):
        # A query of the form 'More than 14 days ago' should generate a max
        # query with the value set to a date 14 days in the past.
        self.dummy.field = 'created'
        self.dummy.setOperation('more')
        self.dummy.setDateRange('-')
        self.dummy.setValue('14')
        expected_begin = DateTime().earliestTime() - 14
        items = self.dummy.getCriteriaItems()
        self.assertEquals(len(items),1)
        query = items[0][1]
        self.assertEquals(query['query'], expected_begin)
        self.assertEquals(query['range'], 'max')

    def test_MoreThanFuture(self):
        # A query of the form 'More than 14 days in the future' should generate
        # a min query with the value set to a date 14 days in the future.
        self.dummy.field = 'created'
        self.dummy.setOperation('more')
        self.dummy.setDateRange('+')
        self.dummy.setValue('14')
        expected_begin = DateTime().earliestTime() + 14
        items = self.dummy.getCriteriaItems()
        self.assertEquals(len(items),1)
        query = items[0][1]
        self.assertEquals(query['query'], expected_begin)
        self.assertEquals(query['range'], 'min')

    def test_MoreThanNow(self):
        # A query of the form 'More than Now' should generate
        # a min query with the value set to the present, regardless of the
        # past future setting.
        self.dummy.field = 'created'
        self.dummy.setOperation('more')
        self.dummy.setDateRange('+')
        self.dummy.setValue('0')
        expected_begin = DateTime().earliestTime()
        items = self.dummy.getCriteriaItems()
        self.assertEquals(len(items),1)
        query = items[0][1]
        self.assertEquals(query['query'].earliestTime(), expected_begin)
        self.assertEquals(query['range'], 'min')
        # Change past/future setting
        self.dummy.setDateRange('-')
        self.assertEquals(query['query'].earliestTime(), expected_begin)
        self.assertEquals(query['range'], 'min')

    def test_MoreThanNow(self):
        # A query of the form 'Less than Now' should generate
        # a max query with the value set to the present, regardless of the
        # past future setting.
        self.dummy.field = 'created'
        self.dummy.setOperation('less')
        self.dummy.setDateRange('+')
        self.dummy.setValue('0')
        expected_begin = DateTime().earliestTime()
        items = self.dummy.getCriteriaItems()
        self.assertEquals(len(items),1)
        query = items[0][1]
        self.assertEquals(query['query'].earliestTime(), expected_begin)
        self.assertEquals(query['range'], 'max')
        # Change past/future setting
        self.dummy.setDateRange('-')
        self.assertEquals(query['query'].earliestTime(), expected_begin)
        self.assertEquals(query['range'], 'max')

tests.append(TestATDateCriteria)


class TestATListCriterion(CriteriaTest):
    klass = ATListCriterion
    title = 'List Criterion'
    meta_type = 'ATListCriterion'
    portal_type = 'ATListCriterion'

    def test_list_query(self):
        self.dummy.field = 'Subject'
        self.dummy.setOperator('or')
        self.dummy.setValue(('1','2','3'))
        items = self.dummy.getCriteriaItems()
        self.assertEquals(len(items),1)
        query = items[0][1]
        field = items[0][0]
        self.assertEquals(field, 'Subject')
        self.assertEquals(query['query'], ('1','2','3'))
        self.assertEquals(query['operator'], 'or')

tests.append(TestATListCriterion)


class TestATSimpleIntCriterion(CriteriaTest):
    klass = ATSimpleIntCriterion
    title = 'Simple Int Criterion'
    meta_type = 'ATSimpleIntCriterion'
    portal_type = 'ATSimpleIntCriterion'

    def test_base_int_query(self):
        self.dummy.field = 'getObjPositionInParent'
        self.dummy.setDirection('')
        self.dummy.setValue(12)
        items = self.dummy.getCriteriaItems()
        self.assertEquals(len(items),1)
        query = items[0][1]
        field = items[0][0]
        self.assertEquals(field, 'getObjPositionInParent')
        self.assertEquals(query['query'], 12)

    def test_int_min(self):
        self.dummy.field = 'getObjPositionInParent'
        self.dummy.setDirection('min')
        self.dummy.setValue(12)
        items = self.dummy.getCriteriaItems()
        self.assertEquals(len(items),1)
        query = items[0][1]
        self.assertEquals(query['query'], 12)
        self.assertEquals(query['range'], 'min')

    def test_int_max(self):
        self.dummy.field = 'getObjPositionInParent'
        self.dummy.setDirection('max')
        self.dummy.setValue(12)
        items = self.dummy.getCriteriaItems()
        self.assertEquals(len(items),1)
        query = items[0][1]
        self.assertEquals(query['query'], 12)
        self.assertEquals(query['range'], 'max')

    def test_int_between(self):
        self.dummy.field = 'getObjPositionInParent'
        self.dummy.setDirection('min:max')
        self.dummy.setValue(12)
        self.dummy.setValue2(17)
        items = self.dummy.getCriteriaItems()
        self.assertEquals(len(items),1)
        query = items[0][1]
        self.assertEquals(query['query'], (12,17))
        self.assertEquals(query['range'], 'min:max')

tests.append(TestATSimpleIntCriterion)


class TestATSimpleStringCriterion(CriteriaTest):
    klass = ATSimpleStringCriterion
    title = 'Simple String Criterion'
    meta_type = 'ATSimpleStringCriterion'
    portal_type = 'ATSimpleStringCriterion'

    def test_string_query(self):
        self.dummy.field = 'Subject'
        self.dummy.setValue('a*')
        items = self.dummy.getCriteriaItems()
        self.assertEquals(len(items),1)
        query = items[0][1]
        field = items[0][0]
        self.assertEquals(field, 'Subject')
        self.assertEquals(query, 'a*')

tests.append(TestATSimpleStringCriterion)


class TestATSortCriterion(CriteriaTest):
    klass = ATSortCriterion
    title = 'Sort Criterion'
    meta_type = 'ATSortCriterion'
    portal_type = 'ATSortCriterion'

    def test_sort_query(self):
        self.dummy.field = 'getObjPositionInParent'
        self.dummy.setReversed(False)
        items = self.dummy.getCriteriaItems()
        self.assertEquals(len(items),1)
        self.assertEquals(items[0][0], 'sort_on')
        self.assertEquals(items[0][1], 'getObjPositionInParent')

    def test_list_query_reversed(self):
        self.dummy.field = 'getObjPositionInParent'
        self.dummy.setReversed(True)
        items = self.dummy.getCriteriaItems()
        self.assertEquals(len(items),2)
        self.assertEquals(items[0][0], 'sort_on')
        self.assertEquals(items[0][1], 'getObjPositionInParent')
        self.assertEquals(items[1][0], 'sort_order')
        self.assertEquals(items[1][1], 'reverse')

tests.append(TestATSortCriterion)


class TestATSelectionCriterion(CriteriaTest):
    klass = ATSelectionCriterion
    title = 'Selection Criterion'
    meta_type = 'ATSelectionCriterion'
    portal_type = 'ATSelectionCriterion'

    #Same as list criterion but without operator and with special vocabulary
    def test_selection_query(self):
        self.dummy.field = 'Subject'
        self.dummy.setValue(('1','2','3'))
        items = self.dummy.getCriteriaItems()
        self.assertEquals(len(items),1)
        query = items[0][1]
        field = items[0][0]
        self.assertEquals(field, 'Subject')
        self.assertEquals(query, ('1','2','3'))

    def test_vocabulary(self):
        #Should return some ids
        self.dummy.field = 'getId'
        self.failUnless(self.dummy.getCurrentValues())

tests.append(TestATSelectionCriterion)


class TestATDateRangeCriterion(CriteriaTest):
    klass = ATDateRangeCriterion
    title = 'Date Range Criterion'
    meta_type = 'ATDateRangeCriterion'
    portal_type = 'ATDateRangeCriterion'

    def test_date_range_query(self):
        self.dummy.field = 'created'
        now = DateTime()
        self.dummy.setStart(now)
        self.dummy.setEnd(now+5)
        items = self.dummy.getCriteriaItems()
        self.assertEquals(len(items),1)
        query = items[0][1]
        field = items[0][0]
        self.assertEquals(field, 'created')
        self.assertEquals(query['query'][0], now)
        self.assertEquals(query['query'][1], now+5)
        self.assertEquals(query['range'], 'min:max')

tests.append(TestATDateRangeCriterion)


class TestATReferenceCriterion(CriteriaTest):
    klass = ATReferenceCriterion
    title = 'Reference Criterion'
    meta_type = 'ATReferenceCriterion'
    portal_type = 'ATReferenceCriterion'

    #Same as list criterion but without operator and with special vocabulary
    def test_reference_query(self):
        self.dummy.field = 'Subject'
        self.dummy.setValue(('1','2','3'))
        items = self.dummy.getCriteriaItems()
        self.assertEquals(len(items),1)
        query = items[0][1]
        field = items[0][0]
        self.assertEquals(field, 'Subject')
        self.assertEquals(query, ('1','2','3'))

tests.append(TestATReferenceCriterion)


class TestATBooleanCriterion(CriteriaTest):
    klass = ATBooleanCriterion
    title = 'Boolean Criterion'
    meta_type = 'ATBooleanCriterion'
    portal_type = 'ATBooleanCriterion'
    
    def test_boolean_query_true(self):
        self.dummy.field = 'isPrincipiaFolderish'
        self.dummy.setBool(True)
        items = self.dummy.getCriteriaItems()
        self.assertEquals(len(items),1)
        query = items[0][1]
        field = items[0][0]
        self.assertEquals(field, 'isPrincipiaFolderish')
        self.assertEquals(query, [1,True,'1','True'])
    
    def test_boolean_query_false(self):
        self.dummy.field = 'isPrincipiaFolderish'
        self.dummy.setBool(False)
        items = self.dummy.getCriteriaItems()
        self.assertEquals(len(items),1)
        query = items[0][1]
        field = items[0][0]
        self.assertEquals(field, 'isPrincipiaFolderish')
        self.assertEquals(query, [0,'',False,'0','False', None, (), [], {}, MV])

tests.append(TestATBooleanCriterion)


class TestATPortalTypeCriterion(CriteriaTest):
    klass = ATPortalTypeCriterion
    title = 'Portal Types Criterion'
    meta_type = 'ATPortalTypeCriterion'
    portal_type = 'ATPortalTypeCriterion'

    #Same as list criterion but without operator and with special vocabulary
    def test_portaltype_query(self):
        self.dummy.field = 'portal_type'
        self.dummy.setValue(('Document','Folder','Topic'))
        items = self.dummy.getCriteriaItems()
        self.assertEquals(len(items),1)
        query = items[0][1]
        field = items[0][0]
        self.assertEquals(field, 'portal_type')
        self.assertEquals(query, ('Document','Folder','Topic'))

    def test_vocabulary(self):
        #Should return standard types, but not blacklisted types
        self.dummy.field = 'portal_type'
        self.failUnless('Document' in self.dummy.getCurrentValues())
        self.failUnless('ATSimpleStringCriterion' not in self.dummy.getCurrentValues())

    def test_types_v_portaltypes(self):
        #Using the Types index as field should cause the vocabulary to use the
        #type Title rather than the type name
        self.dummy.field = 'portal_type'
        self.failUnless('Large Plone Folder' in self.dummy.getCurrentValues())
        self.failUnless('Large Folder' not in self.dummy.getCurrentValues())
        self.dummy.field = 'Type'
        self.failUnless('Large Plone Folder' not in self.dummy.getCurrentValues())
        self.failUnless('Large Folder' in self.dummy.getCurrentValues())
        #ensure that blacklisted types aren't here either
        self.failUnless('Simple String Criterion' not in self.dummy.getCurrentValues())

tests.append(TestATPortalTypeCriterion)


class TestATCurrentAuthorCriterion(CriteriaTest):
    klass = ATCurrentAuthorCriterion
    title = 'Current Author Criterion'
    meta_type = 'ATCurrentAuthorCriterion'
    portal_type = 'ATCurrentAuthorCriterion'

    def afterSetUp(self):
        CriteriaTest.afterSetUp(self)
        self.portal.acl_users._doAddUser('member', 'secret', ['Member'], [])
        self.portal.acl_users._doAddUser('reviewer', 'secret', ['Reviewer'], [])

    def test_author_query(self):
        self.dummy.field = 'creator'
        self.login('member')
        items = self.dummy.getCriteriaItems()
        self.assertEquals(len(items),1)
        query = items[0][1]
        field = items[0][0]
        self.assertEquals(field, 'creator')
        self.assertEquals(query, 'member')
        self.login('reviewer')
        items = self.dummy.getCriteriaItems()
        self.assertEquals(len(items),1)
        query = items[0][1]
        field = items[0][0]
        self.assertEquals(field, 'creator')
        self.assertEquals(query, 'reviewer')

tests.append(TestATCurrentAuthorCriterion)


if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        for test in tests:
            suite.addTest(unittest.makeSuite(test))
        return suite