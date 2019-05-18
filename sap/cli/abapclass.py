"""ADT proxy for ABAP Class (OO)"""

import sap.adt
import sap.adt.wb
import sap.cli.core
import sap.cli.object


SOURCE_TYPES = ['main', 'definitions', 'implementations', 'testclasses']


class CommandGroup(sap.cli.object.CommandGroupObjectMaster):
    """Commands for Class"""

    def __init__(self):
        super(CommandGroup, self).__init__('class')

        self.define()

    def instance(self, connection, name, args, metadata=None):
        package = None
        if hasattr(args, 'package'):
            package = args.package

        clas = sap.adt.Class(connection, name, package=package, metadata=metadata)

        typ = None
        if args.name == '-':
            _, suffix = sap.cli.object.object_name_from_source_file(args.source)

            if suffix == 'clas.abap':
                return clas

            typ = {
                'clas.locals_def.abap': 'definitions',
                'clas.testclasses.abap': 'testclasses',
                'clas.locals_imp.abap': 'implementations'}[suffix]
        elif not hasattr(args, 'type'):
            return clas
        else:
            typ = args.type

        if typ == 'definitions':
            return clas.definitions

        if typ == 'implementations':
            return clas.implementations

        if typ == 'testclasses':
            return clas.test_classes

        return clas

    def define_read(self, commands):
        read_cmd = super(CommandGroup, self).define_read(commands)
        read_cmd.insert_argument(1, '--type', default=SOURCE_TYPES[0], choices=SOURCE_TYPES)

        return read_cmd

    def define_write(self, commands):
        write_cmd = super(CommandGroup, self).define_write(commands)
        write_cmd.insert_argument(1, '--type', default=SOURCE_TYPES[0], choices=SOURCE_TYPES)

        return write_cmd


@CommandGroup.argument('name')
@CommandGroup.command()
def attributes(connection, args):
    """Prints out some attributes of the given class.
    """

    clas = sap.adt.Class(connection, args.name)
    clas.fetch()

    print(f'Name       : {clas.name}')
    print(f'Description: {clas.description}')
    print(f'Responsible: {clas.responsible}')
    # pylint: disable=no-member
    print(f'Package    : {clas.reference.name}')
