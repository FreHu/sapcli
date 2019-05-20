"""ADT Object CLI templates"""

import sys
import os
import collections

import sap.cli.core
from sap.cli.core import InvalidCommandLineError
import sap.errors

import sap.adt
import sap.adt.wb


_NAME_INDEX = 0


def object_name_from_source_file(filesystem_path):
    """Splits the given file system path into object name and suffix.

       It is expected that the object name makes the file name prefix up to
       the first dot.

       Example:
         ./src/object.abap
                      ^^^^--- suffix (the 2nd return value)
               ^^^^^^-------- object name (the 1st return value)
    """

    basename = os.path.basename(filesystem_path)
    parts = filesystem_path.split('.', 1)

    if len(parts) == 1:
        raise sap.errors.SAPCliError(f'{basename} does not match the pattern NAME.SUFFIX')

    if not parts[_NAME_INDEX]:
        raise sap.errors.SAPCliError(f'{basename} does not contain NAME from the pattern NAME.SUFFIX')

    return parts


def write_args_to_objects(command, args):
    """Converts parameters of the action 'write object' into a iteration of
       objects with the text content
    """

    name = args.name
    text = None

    if name == '-':
        for filepath in args.source:
            if filepath == '-':
                raise InvalidCommandLineError('Source file cannot be - when Object name is - too')

            with open(filepath, 'r') as filesrc:
                text = filesrc.readlines()

            yield return (command.instance_from_file_path(connectoin, filepath, args), text)

    elif len(args.source) == 1:
        if args.source[0] == '-':
            text = sys.stdin.readlines()
        else:
            with open(args.source[0], 'r') as filesrc:
                text = filesrc.readlines()

        yield return (command.instance(connection, args.name, args), text)

    else:
        raise InvalidCommandLineError('Source file can be a list when Object name is -')


class CommandGroupObjectTemplate(sap.cli.core.CommandGroup):
    """Template Class converting command line parameters to ADT Object methods
       calls.
    """

    def instance(self, connection, name, args, metadata=None):
        """Returns new instance of the ADT Object proxy class"""

        raise NotImplementedError()

    def instance_from_file_path(self, connection, filepath, args, metadata=None):
        """Returns new instance of the ADT Object proxy class
           where the object name should be deduced from
           the given file path.
        """

        name, _ = object_name_from_source_file(filepath)
        obj = self.instance(connection, name, args, metadata=metadata)

    def build_new_metadata(self, connection, args):
        """Creates an instance of the ADT Object Metadata class for a new object"""

        raise NotImplementedError()

    def define_create(self, commands):
        """Declares the Create command with its parameters and returns
           the definition.

           Notice, that this command does not declare the parameter package
           which should be create by descendants if necessary.
        """

        create_cmd = commands.add_command(self.create_object, name='create')
        create_cmd.append_argument('name')
        create_cmd.append_argument('description')
        create_cmd.declare_corrnr()

        return create_cmd

    def define_read(self, commands):
        """Declares the Read command with its parameters and returns
           the definition
        """

        read_cmd = commands.add_command(self.read_object_text, name='read')
        read_cmd.append_argument('name')

        return read_cmd

    def define_write(self, commands):
        """Declares the Write command with its parameters and returns
           the definition.
        """

        write_cmd = commands.add_command(self.write_object_text, name='write')
        write_cmd.append_argument('name',
                                  help='an object name or - for getting it from the source file name')
        write_cmd.append_argument('source', nargs='+',
                                  help='a path or - for stdin; multiple allowed only when name = -')
        write_cmd.append_argument('-a', '--activate', action='store_true',
                                  default=False, help='activate after write')
        write_cmd.declare_corrnr()

        return write_cmd

    def define_activate(self, commands):
        """Declares the Activate command with its parameters and returns the
           definition.

           Notice that it allows multiple names on input.
        """

        activate_cmd = commands.add_command(self.activate_objects, name='activate')
        activate_cmd.append_argument('name', nargs='+')

        return activate_cmd

    def define(self):
        """Defines the commands Create, Read, Write, and Activate and returns
           the command list
        """

        cls = self.__class__

        if hasattr(cls, '_instance'):
            return None

        # pylint: disable=protected-access
        cls._instance = self

        commands = cls.get_commands()

        self.define_create(commands)
        self.define_read(commands)
        self.define_write(commands)
        self.define_activate(commands)

        return commands

    def build_new_object(self, connection, args, metadata):
        """Creates an instance of the ADT Object proxy class for a new object"""

        return self.instance(connection, args.name, args, metadata=metadata)

    def create_object(self, connection, args):
        """Creates the given object."""

        metadata = self.build_new_metadata(connection, args)
        obj = self.build_new_object(connection, args, metadata)

        obj.description = args.description

        obj.create(corrnr=args.corrnr)

    def read_object_text(self, connection, args):
        """Retrieves the request command prints it out based on command line
           configuration.
        """

        obj = self.instance(connection, args.name, args)
        print(obj.text)

    def write_object_text(self, connection, args):
        """Changes source code of the given program include"""

        toactivate = collections.OrderedDict()

        for obj in write_args_to_objects(self, args):
            with obj.open_editor(corrnr=args.corrnr) as editor:
                editor.write(''.join(text))

            toactivate[obj.name] = obj

        if args.activate:
            for obj in toactivate.values():
                sap.adt.wb.activate(obj)

    def activate_objects(self, connection, args):
        """Actives the given object."""

        for name in args.name:
            obj = self.instance(connection, name, args)
            sap.adt.wb.activate(obj)


# pylint: disable=abstract-method
class CommandGroupObjectMaster(CommandGroupObjectTemplate):
    """Commands for objects that belongs to a package.

       The class CommandGroupObjectTemplate defines the command create without the
       parameter packages because there are objects that belongs to a container
       object (i.e. Function Module).
    """

    def build_new_metadata(self, connection, args):
        """Creates an instance of the ADT Object Metadata class for a new object"""

        return sap.adt.ADTCoreData(language='EN', master_language='EN',
                                   package=args.package.upper(), responsible=connection.user.upper())

    def define_create(self, commands):
        """Calls the super's define_create and inserts the parameter package
           right behind the parameter description
        """

        create_cmd = super(CommandGroupObjectMaster, self).define_create(commands)

        create_cmd.insert_argument(2, 'package')

        return create_cmd
