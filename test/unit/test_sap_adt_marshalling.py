#!/bin/python

import unittest

from sap import get_logger
from sap.adt import ADTObject, ADTObjectType, ADTCoreData, OrderedClassMembers
from sap.adt.objects import XMLNamespace
from sap.adt.annotations import xml_element, xml_attribute
from sap.adt.marshalling import Marshal, Element, adt_object_to_element_name, ElementHandler


class Dummy(ADTObject):

    OBJTYPE = ADTObjectType(
        'CODE',
        'prefix/dummy',
        XMLNamespace('dummyxmlns', 'http://www.sap.com/adt/xmlns/dummy'),
        'application/vnd.sap.adt.test.elements.v2+xml',
        {'text/plain': 'source/main'},
        'dummyelem'
    )

    class Nested(metaclass=OrderedClassMembers):

        class SuperNested(metaclass=OrderedClassMembers):

            @xml_attribute('sup_nst_fst')
            def yetanother(self):
                return 'yetanother'

        @xml_attribute('nst_fst')
        def first(self):
            return 'nst_fst_val'

        @xml_attribute('nst_scn')
        def second(self):
            return 'nst_scn_val'

        @xml_element('child_nst')
        def supernested(self):
            return Dummy.Nested.SuperNested()

    def __init__(self):
        super(Dummy, self).__init__(
            None, 'dmtname',
            metadata=ADTCoreData(
                package='testpkg',
                description='Description',
                language='CZ',
                master_language='EN',
                master_system='NPL',
                responsible='FILAK'
            )
        )

        self._nested = Dummy.Nested()

    @xml_attribute('attr_first')
    def first(self):
        return '11111'

    @xml_attribute('attr_second')
    def second(self):
        return '22222'

    @xml_attribute('attr_third', deserialize=False)
    def third(self):
        return '3333'

    @xml_element('first_elem')
    def value(self):
        return self._nested

    @xml_element('readonly_elem', deserialize=False)
    def readonly(self):
        return Dummy.Nested()


class DummyWithSetters(ADTObject):

    OBJTYPE = ADTObjectType(
        'CODE',
        'prefix/dummy',
        XMLNamespace('dummyxmlns', 'http://www.sap.com/adt/xmlns/dummy'),
        'application/vnd.sap.adt.test.elements.v2+xml',
        {'text/plain': 'source/main'},
        'dummyelem'
    )

    class Nested(metaclass=OrderedClassMembers):

        class SuperNested(metaclass=OrderedClassMembers):

            def __init__(self):
                self._yetanother = None

            @xml_attribute('sup_nst_fst')
            def yetanother(self):
                return self._yetanother

            @yetanother.setter
            def yetanother(self, value):
                self._yetanother = value

        def __init__(self):
            self._child = DummyWithSetters.Nested.SuperNested()
            self._first = None
            self._second = None

        @xml_attribute('nst_fst')
        def first(self):
            return self._first

        @first.setter
        def first(self, value):
            self._first = value

        @xml_attribute('nst_scn')
        def second(self):
            return self._second

        @second.setter
        def second(self, value):
            self._second = value

        @xml_element('child_nst')
        def supernested(self):
            return self._child


    def __init__(self):
        super(DummyWithSetters, self).__init__(
            None, 'dmtname',
            metadata=ADTCoreData(
                package='testpkg',
                description='Description',
                language='CZ',
                master_language='EN',
                master_system='NPL',
                responsible='FILAK'
            )
        )

        self._nested = DummyWithSetters.Nested()
        self._first = None
        self._second = None

    @xml_attribute('attr_first')
    def first(self):
        return self._first

    @first.setter
    def first(self, value):
        self._first = value

    @xml_attribute('attr_second')
    def second(self):
        return self._second

    @second.setter
    def second(self, value):
        self._second = value

    @xml_attribute('attr_third', deserialize=False)
    def third(self):
        return 'EEE'

    @xml_element('first_elem')
    def value(self):
        return self._nested

    @xml_element('readonly_elem', deserialize=False)
    def readonly(self):
        # If there is a bug in deserialization, the return None will reveal
        # that Marshal tried to modify read-only property
        return None



class DummyChild(metaclass=OrderedClassMembers):

    instances = None

    def __init__(self):
        if DummyChild.instances is None:
            DummyChild.instances = list()
        DummyChild.instances.append(self)

        get_logger().debug('New instance')
        self._attribute = None

    @xml_attribute('attribute')
    def attribute(self):
        return self._attribute

    @attribute.setter
    def attribute(self, value):
        self._attribute = value


class DummyWithChildFactory(ADTObject):

    OBJTYPE = ADTObjectType(
        'CODE',
        'prefix/dummy',
        XMLNamespace('dummyxmlns', 'http://www.sap.com/adt/xmlns/dummy'),
        'application/vnd.sap.adt.test.elements.v2+xml',
        {'text/plain': 'source/main'},
        'dummyelem'
    )

    def __init__(self):
        self._child = None
        self._child_setter = None

    @xml_element('child', factory=DummyChild)
    def child(self):
        return self._child

    @xml_element('child_setter', factory=DummyChild)
    def child_setter(self):
        get_logger().debug('Get instance')
        return self._child_setter

    @child_setter.setter
    def child_setter(self, value):
        get_logger().debug('Set instance')
        self._child_setter = value


class DummyADTCore(ADTObject):

    OBJTYPE = ADTObjectType(
        None,
        None,
        XMLNamespace('adtcore', 'http://www.sap.com/adt/core'),
        None,
        None,
        'root'
    )

    def __init__(self):
        super(DummyADTCore, self).__init__(None, None)


class DummyContainerItem(metaclass=OrderedClassMembers):

    def __init__(self, no):
        self._no = no

    @xml_attribute('number')
    def attribute(self):
        return self._no


class DummyContainer(ADTObject):

    OBJTYPE = ADTObjectType(
        None,
        None,
        XMLNamespace('adtcore', 'http://www.sap.com/adt/core'),
        None,
        None,
        'container'
    )

    def __init__(self):
        super(DummyContainer, self).__init__(None, None)

    @xml_element('item')
    def items(self):
        return [DummyContainerItem('1'), DummyContainerItem('2'), DummyContainerItem('3')]


class TestADTAnnotation(unittest.TestCase):


    def test_tree_generation(self):
        obj = Dummy()
        marshal = Marshal()
        xmltree = marshal._object_to_tree(obj)

        self.assertEqual(xmltree.name, 'dummyxmlns:dummyelem')
        self.assertEqual(xmltree.attributes['attr_first'], '11111')
        self.assertEqual(xmltree.attributes['attr_second'], '22222')
        self.assertEqual(xmltree.attributes['attr_third'], '3333')

        self.assertEqual(xmltree.children[0].name, 'adtcore:packageRef')

        self.assertEqual(xmltree.children[1].name, 'first_elem')
        self.assertEqual(xmltree.children[1].attributes['nst_fst'], 'nst_fst_val')
        self.assertEqual(xmltree.children[1].attributes['nst_scn'], 'nst_scn_val')

        self.assertEqual(xmltree.children[1].children[0].name, 'child_nst')
        self.assertEqual(xmltree.children[1].children[0].attributes['sup_nst_fst'], 'yetanother')

    def test_xml_formatting(self):
        marshal = Marshal()
        elem = Element('root')
        elem.add_attribute('one', '1')
        elem.add_attribute('two', '2')
        child = elem.add_child('child')
        xml = marshal._tree_to_xml(elem)
        self.assertEqual(xml, '<?xml version="1.0" encoding="UTF-8"?>\n<root one="1" two="2">\n<child/>\n</root>')

    def test_element_handler(self):
        adt_object = DummyWithSetters()
        name = '/' + adt_object_to_element_name(adt_object)
        self.assertEqual('/dummyxmlns:dummyelem', name)

        elements = dict()
        handler = ElementHandler(name, elements, lambda: adt_object)
        elements[name] = handler
        handler.new()

        self.assertIn(f'{name}/first_elem', elements)

        handler.set('attr_first', '1st')
        self.assertEqual(adt_object.first, '1st')

        handler.set('attr_second', '2nd')
        self.assertEqual(adt_object.second, '2nd')

        child_handler = elements[f'{name}/first_elem']
        child_handler.new()

        self.assertIn(f'{name}/first_elem/child_nst', elements)

        child_handler.set('nst_fst', '1.')
        self.assertEqual(adt_object.value.first, '1.')

        child_handler.set('nst_scn', '2.')
        self.assertEqual(adt_object.value.second, '2.')

        grand_child_handler = elements[f'{name}/first_elem/child_nst']
        grand_child_handler.new()

        grand_child_handler.set('sup_nst_fst', 'X')
        self.assertEqual(adt_object.value.supernested.yetanother, 'X')


    def test_deserialization(self):
        obj = Dummy()
        marshal = Marshal()
        xml_data = marshal.serialize(obj)

        clone = DummyWithSetters()
        #get_logger().setLevel(0)
        ret = Marshal.deserialize(xml_data, clone)
        self.assertEqual(clone, ret)

        self.assertEqual(obj.first, clone.first)
        self.assertEqual(obj.second, clone.second)
        self.assertEqual('EEE', clone.third)
        self.assertEqual(obj.value.first, clone.value.first)
        self.assertEqual(obj.value.second, clone.value.second)
        self.assertEqual(obj.value.supernested.yetanother, clone.value.supernested.yetanother)

    def test_deserialize_with_factory(self):
        dummy = DummyWithChildFactory()

        #get_logger().setLevel(0)
        Marshal.deserialize("""<?xml version="1.0" encoding="UTF-8"?>
<dummyxmlns:dummyelem>
  <child attribute="implicit"/>
  <child_setter attribute="setter"/>
</dummyxmlns:dummyelem>
""", dummy)

        self.assertEqual(DummyChild.instances[0].attribute, 'implicit')
        self.assertEqual(dummy.child_setter.attribute, 'setter')

    def test_serialize_adtcore_and_no_code(self):
        obj = DummyADTCore()
        act = Marshal().serialize(obj)

        self.assertEqual(act, '''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:root xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:packageRef/>
</adtcore:root>''')

    def test_serialize_list(self):
        container = DummyContainer()

        get_logger().setLevel(0)
        act = Marshal().serialize(container)

        self.assertEqual(act, '''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:container xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:packageRef/>
<item number="1"/>
<item number="2"/>
<item number="3"/>
</adtcore:container>''')


if __name__ == '__main__':
    unittest.main()
