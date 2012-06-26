# -*- coding: utf-8 -*-
'''
Created on 02/03/2012

@author: moi
'''
__author__ = "Moises P. Sena"
__version__ = "1.0"

import optparse
import textwrap

class Formatter(optparse.IndentedHelpFormatter):

    def __init__(self, *args, **kwargs):

        optparse.IndentedHelpFormatter.__init__(self, *args, **kwargs)
        self.wrapper = textwrap.TextWrapper(width=self.width)

    def _formatter(self, text):
        return '\n'.join(['\n'.join(p) for p in map(self.wrapper.wrap,
                self.parser.expand_prog_name(text).split('\n'))])

    def format_description(self, description):
        if description:
            return self._formatter(description) + '\n'
        else:
            return ''

    def format_epilog(self, epilog):
        if epilog:
            return '\n' + self._formatter(epilog) + '\n'
        else:
            return ''

    def format_usage(self, usage):
        return self._formatter(optparse._("Usage: %s\n") % usage)

    def format_option(self, option):
        # Ripped and modified from Python 2.6's optparse's HelpFormatter
        result = []
        opts = self.option_strings[option]
        opt_width = self.help_position - self.current_indent - 2
        if len(opts) > opt_width:
            opts = "%*s%s\n" % (self.current_indent, "", opts)
            indent_first = self.help_position
        else:                                             # start help on same line as opts
            opts = "%*s%-*s    " % (self.current_indent, "", opt_width, opts)
            indent_first = 0
        result.append(opts)
        if option.help:
            help_text = self.expand_default(option)
            # Added expand program name
            help_text = self.parser.expand_prog_name(help_text)
            # Modified the generation of help_line
            help_lines = []
            wrapper = textwrap.TextWrapper(width=self.help_width)
            for p in map(wrapper.wrap, help_text.split('\n')):
                if p:
                    help_lines.extend(p)
                else:
                    help_lines.append('')
            # End of modification
            result.append("%*s%s\n" % (indent_first, "", help_lines[0]))
            result.extend(["%*s%s\n" % (self.help_position, "", line)
                                         for line in help_lines[1:]])
        elif opts[-1] != "\n":
            result.append("\n")
        return "".join(result)
