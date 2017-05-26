Language Reference
==================

General Language Attributes
---------------------------
Execution is sequential. All transient variables are implicitly declared upon
the first assignment. Any subsequent assignment simply re-assign the same
variable. A re-assignment of a variable to a different type is not allowed.
A stack execution model is assumed. Variables are pushed on the stack as they
are implicitly declared and are popped off the stack as they fall out of scope.
Any variable implicitly declared inside of a block falls out of scope when the
end of the block is encountered.

White space is treated as a token delimiter. Statements are intended to be
readable as a sentence so keywords are used in groups to provide verb phrases
or prepositional phrases when combined with variables and model element
references.

Keywords and variables are case **insensitive**. Names can be made up of any
alpha (a-z, A-Z) or numeric (0-9) characters or underscore (_) character. Names
cannot begin with a numeric character. Names cannot conflict with keywords.
Classes in the model are specified by using the class keyletters.

Literal Text
------------
Literal text is plain ASCII text that is eventually written to files with the
`emit to file` statement. Any line in the processed file which is not a control
statement is treated as literal text. Any line beginning with a dot character
(.) as the first non-white space character is a control statement, except those
lines which begin with the dot dot character sequence (..).

Lines 2-4 of the following rule are literal text lines. These lines are stored
in a buffer than can be emitted to a file at any time by using the `emit to file`
statement. The first line is a control statement used to comment the rule.

.. code-block:: pyrsl
   :linenos:
   
   .// comment the rule file
   This is a literal text line
   and so is this. Each of these lines are stored in a buffer that
   can be emitted to a file using the .emit statement.
       
A literal text line with the dot dot character sequence as the first non-white
space characters results in the dot character being emitted. A dot character
anywhere else in the literal text line results in a dot character being emitted
(i.e. no special treatment).

Literal text can contain `Substitution Variables`_. Substitution variables are
denoted with the `${<variable_name>}` character sequence. This means that the
dollar sign character ($) is a special character which denotes the beginning of
a substitution variable. The `$$` character sequence anywhere in a literal text
line results in one dollar character being emitted.

Newline characters at the end of a line of literal text are passed through to
the emitted output. If you do not want a newline at the end of an emitted line
(presumably due to control statement constraints), then place a backslash
character (\\) as the last character of the literal text line. The `\\\\`
character sequence as the last two characters of the literal text line results
in one backslash character and one newline character as the last characters of
an emitted line. The `\\\\\\` character sequence as the last three characters of
a line of literal text results in one backslash character as the last character
of an emitted line with no newline character.

====================  =====================  ===================================== 
Character             Position               To Generate Character at Position Use
====================  =====================  =====================================
.                     First Non-White Space  `..`
$                     Any                    `$$`
\\ (with new line)    Last                    `\\\\`
\\ (without newline)  Last                    `\\\\\\`
====================  =====================  =====================================

Data Access Control Statements
------------------------------
Data access control statements include the following:

* Instance selection statements allow for the selecting of instances from the
  model. Instances are either returned in an instance reference set, in the
  case of a `select many`, or as an instance reference, in the case of `select
  one` and `select any`.

* Instance set iteration statements allow for iteration over a set of instances
  contained in an instance reference set. Class attribute access statements are
  used to read and write attribute data of instances in the model.

Instance Selection
^^^^^^^^^^^^^^^^^^
Instances may be selected from the model by using the key letters of the class
directly, or by chaining through class keyletter/association pairs using an
instance reference or instance reference set as a starting point.

The following two statements are used to select instances based on the key
letters alone:

.. code-block:: pyrsl

    .select any  <inst_ref_var>     from instances of <class_keyletters> [ where (<condition>) ]
    .select many <inst_ref_set_var> from instances of <class_keyletters> [ where (<condition>) ]
       
The following instance selection statements make direct use of chaining through
key letter/association pairs to select an instance or set of instances:

.. code-block:: pyrsl

    .select one  <inst_ref_var>     related by <inst_chain> [ where (<condition>) ]
    .select any  <inst_ref_var>     related by <inst_chain> [ where (<condition>) ]
    .select many <inst_ref_set_var> related by <inst_chain> [ where (<condition>) ]
       
`<inst_ref_var>` specifies an instance reference variable name used in the
selection. After the select, the variable contains a reference to zero or one
instances. Zero if an instance was not found, one if the instance was found.

`<inst_ref_set_var>` specifies an instance reference set variable name used in
the selection. After the select, the variable contains a reference to zero, one,
or several instances.

`<inst_chain>` is a string containing key letter/association number pairs
separated by the `->` character sequence. `inst_chain` specifies an unbroken
navigation from the instance reference variable or instance reference set
variable to the destination instance.

`<class_keyletters>` are the keyletters of a class in the model.

`<condition>` specifies an expression with a boolean result. `<condition>`
always takes the form of a where clause that discriminates on a attribute of
the destination class using the `selected` keyword.

**Examples**

To select an aplication class in the BridgePoint metamodel named "Dog":

.. code-block:: pyrsl

    .select any class from instances of O_OBJ where (selected.Name == "Dog")

To select the set of application classes in the BridgePoint metamodel:

.. code-block:: pyrsl

    .select many class_set from instances of O_OBJ

To select the set of attributes related to an arbitrary class instance
`class_inst` in the BridgePoint metamodel:

.. code-block:: pyrsl

    .select any class_inst from instances of O_OBJ
    .select many attr_set related by class_inst->O_ATTR[R102]

To select the set of associations in which the class instance `class_inst` is
involved:

.. code-block:: pyrsl

    .select many rel_set related by class_inst->R_OIR[R201]->R_REL[R201]

.. hint::
   The navigation through the association R201 was in 2 steps.
   First to the associative-link class and then to the other side of
   the association. If you are wondering where to find association R201, 
   please look in the BridgePoint metamodel.

   Recent versions of the language allow navigation across association classes
   without explicitly going via the association class, e.g.

   .. code-block:: pyrsl

      .select many rel_set related by class_inst->R_REL[R201]
     
Instance Reference and Instance Reference Set Variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The resulting `<inst_ref_var>` or `<inst_ref_set_var>` is a transient variable
which follows the implicit declaration rule. When the resulting `<inst_ref_var>`
or `<inst_ref_set_var>` is being implicitly declared (used for the first time),
the referred to class of the transient variable is set according to the result
of the `select`. When the resulting `<inst_ref_var>` or `<inst_ref_set_var>` is
being reassigned, the referred to class of the new selection must match that of
the transient variable.

Instance Chains
^^^^^^^^^^^^^^^
The related by form of the `select` statement uses an instance chain to specify
a path through the related instances. An instance chain is simply a sequence of
class key letter/association number pairs which specify the path from the source
instance to the destination class. The result of a select is zero, one or more
instances of the last class of the chain.

The syntax of the instance chain places the focus on the classes of the chain
(specified by the class keyletters) because the instances of the chain are class
instances. The `[]` syntax is intended to indicate access into a table of that
classes instances. The contents of the `[]` is a specification of which
instances are being accessed, since the instances are accessed via an
association, the contents of the `[]` is the association traversal specification.

The association traversal specification can be specified as `R<number>` or 
`R<number>.'<direction>'` where `R<number>` is the association number as it
appears in the model. `<direction>` is a specification of the direction of the
traversal for the association in terms of an association phrase. The
`<direction>` is used when traversing a reflexive association, i.e., an
association in which a class is related to itself. `<direction>` is needed so
that the reflexive association can be traversed in each direction. Examples of
reflexive associations in the BridgePoint metamodel are R103 (to specify order
of attributes) and R112 (to specify order of association numbers).

The following example selects the previous attribute instance given the current
attribute instance:

.. code-block:: pyrsl

    .select one prev_attr related by curr_attr->O_ATTR[R103.'precedes']

The navigation spec: `->O_ATTR[R103.'precedes']` use the association phrase
to read the navigation from left to right, with the association phrase as the
verb in the middle: start with the instance reference variable prev_attr, apply
the association phrase, and end with the instance chain source instance
reference variable name. The select statement navigation above reads prev_attr
precedes curr_attr. Since we are looking for the attribute that precedes the
current attribute we know that our select statement is properly formed.

If we then wanted to get back to `curr_attr` from `prev_attr` we could
write the following:

.. code-block:: pyrsl

    .select one next_attr related by prev_attr->O_ATTR[R103.'succeeds']

The instance reference `next_attr` is the same instance as `curr_attr` from
the previous `select` statement.

.. warning::
   In recent versions of the language, the phrases you specify in reflexive
   navigations has been swapped to be in line with the Object Action Language
   (OAL) used in BridgePoint.

Chain Multiplicity & Conditionality
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The multiplicity of an instance chain is zero or one if the starting instance
variable has a multiplicity of zero or one, and all association traversals in
the chain result have multiplicity zero or one. Otherwise, the multiplicity of
the instance chain is zero, one, or several (many).

The keyword `one` should only be used with an instance chain of multiplicity
zero or one, whereas the keywords `any` and `many` can only be used with
an instance chain of multiplicity zero, one, or many.

The conditionality of an instance chain is unconditional if all association
traversals in the chain are unconditional; otherwise, the instance chain is
conditional. The conditionality determines how many instances are returned. If
any conditional associations occur in the instance chain to the target, zero
instances may be returned by the select statement. In this case the result of
the select should always be checked for instances before being used.

Where Clause
^^^^^^^^^^^^
The where clause `<condition>` is used to filter out a subset of the instances
selected in the `select from instances of` or `select related by` statements.
`<condition>` is applied separately to each instance in the source set. When
`<condition>` is `true`, the matching instance or instances are
placed in the instance reference or instance reference set variable. Instances
for which <condition> is `false` are not included in the result.

`<condition>` is a boolean expression. The current instance being selected is
referred to by the selected keyword.

**Examples**

To select the set of application attributes named "ID" in the BridgePoint
metamodel:

.. code-block:: pyrsl

    .select many attr_set from instances of O_ATTR where (selected.Name == "ID")

To select all application attributes in classes with keyletters DOG:

.. code-block:: pyrsl

    .select many attr_set from instances of O_ATTR where ("${selected->O_OBJ[R102]}.Key_Lett" == "DOG")

.. note::
   The preceding example uses an instance substitution variable in a quoted
   string and an instance chain within the substitution variable.

Instance Set Iteration
^^^^^^^^^^^^^^^^^^^^^^
**The For Statement**

Once a set of instances has been selected, iteration statements can be written
to iterate over each of the instances in the set. The control statement which
supports this is:

.. code-block:: none

    .for each <inst_ref_var> in <inst_ref_set_var>
        <stmt_blck>
    .end for

`<inst_ref_var>` is an instance reference variable. Each time the for statement
is evaluated, this variable is set to next instance in the set.

`<inst_ref_set_var>` is an instance reference set that contains zero, one or
more instances.

`<stmt_blck>` is a block of any number of control statements.

The statements in the for structure are executed once for each instance in the
set. The iterations are sequential in a repeatable order, i.e., the order of the
instances in a set are consistent from one execution to another.
   
**Examples**

.. code-block:: pyrsl

    Beginning of List of Class Names
    .select many class_set from instances of O_OBJ
    .for each class_inst in class_set
        Class name is ${class_inst.Name}
    .end for
     End of List of Class Names

The example above results in the name of each class being placed on a separate
line in the output buffer. Each time the above example is executed, the order
of the class names is guaranteed to be the same.


.. warning::
   Generelly, the order in which instances are created (and thus serialized)
   determine the order in which they appear in sets. Consequently, the ordering
   between consecutive executions is only preserved if thier input are the same.
   This, however, may differ between implementations of the language.
   
The variable `<inst_ref_var>` is scoped within the `<stmt_blck>` , i.e., it
goes out of scope after the `end for` statement. However, if the scope of 
`<inst_ref_var>` needs to extend beyond the end, then define
`<inst_ref_var>` prior to the for statement. In the previous example,
`class_inst` is out of scope (and no longer on the stack) when the `End of List
of Class Names` literal text line is reached.

In the following example, `class_inst` is still in scope (and still on the stack)
when the `End of List of Class Names` literal text line is reached.

.. code-block:: pyrsl

    Beginning of List of Class Names
    .select any  class_inst from instances of O_OBJ
    .select many class_set  from instances of O_OBJ
    .for each class_inst in class_set
        Class name is ${class_inst.Name}
    .end for
    Last Class name is ${class_inst.Name}

The following statement is provided to break out of the iteration through the
ordered set, presumably because you have found what you were looking for.

.. code-block:: pyrsl

    .break for

.. hint::
   It is sometimes desirable to declare an instance handle that is empty. This
   is usually done with a `select` statement and a `where` clause that always
   evaluates to `false`, e.g.

   .. code-block:: pyrsl

          .select any inst from instances of O_OBJ where (false)
   
**The While Statement**

The `while` statement provides a general purpose iteration mechanism. This
complements the other iteration mechanism, the `for each` statement. The `for
each` statement is a specific purpose iteration mechanism to iterate through an
instance reference set. The syntax of the `while` statement is as follows:

.. code-block:: pyrsl

    .while (<condition>)
        .// Do something
    .end while

The statements between `while` and `end while` are executed in sequence
until `<condition>` evaluates to `false`. The condition is checked before the
first iteration.

A `break while` statement is available, providing an alternative technique
to end the iteration. The syntax of the `break while` statement is as follows:

.. code-block:: pyrsl

    .while (<condition>)
        .// Do something
        .break while
        .// Do something more
	.break
    .end while
       
When executed, the `break while` statement causes control to be transferred to
the statement after the `end while` corresponding to the innermost executing
`while` statement. For example:
   
.. code-block:: pyrsl

    .assign count = 1
    .while (count < 10)             .// while 1
        .while (1 == 1)             .// while 2
            .if (<condition>)
                .break while        .// break 2
            .end if
        .end while                  .// end while 2
        .if (<condition2>)
            .break while            .// break 1
        .end if
    .end while                      .// end while1 

Execution of break 2 causes control to transfer to the statement following 
end while 2, whereas execution of break 1 causes control to transfer to the
statement following end while 1.

Class Attribute Access
^^^^^^^^^^^^^^^^^^^^^^
Attribute access statements take the form of:

.. code-block:: pyrsl

    .assign transient = <inst_ref_var>.<attribute>

where `<inst_ref_var>` is the instance reference variable that refers to an
instance. `<attribute>` is the name of a valid attribute for the instance.


Class Instance Creation
^^^^^^^^^^^^^^^^^^^^^^^
The `create` statement supports creation of instances in the model:

.. code-block:: pyrsl

    .create object instance <inst_ref_var> of <class_keyletters>

where `<inst_ref_var>` is an instance reference variable name that refers to
the to-be created instance. `<class_keyletters>` are the keyletters of a
class.

**Examples**

To create an instance of O_OBJ metamodel class:

.. code-block:: pyrsl

    .create object instance class_inst of O_OBJ
    .assign class_inst.Name = "foo"
    .assign class_inst.Numb = 27
    .assign class_inst.Key_Lett = "F"
    .assign class_inst.Descrip = ""


Relation Control Statements
---------------------------

Assignment Control Statement
-----------------------------
The `assign` statement makes use of `Expressions`_ and have the following syntax:

.. code-block:: pyrsl
   
   .assign <variable> = <expression>

where `<variable>` is a data item, i.e., a class attribute, fragment attribute,
or transient variable. `<expression>` is an expression, usually a calculation
using class attribute access and literal values.

When `<variable>` is a class attribute, the data type of `<expression>` must be
compatible with the data type of `<variable>`.

If `<variable>` is a transient variable, then the transient variable follows the
implicit declaration rule. When a transient variable is being implicitly
declared (assigned for the first time), the data type of the transient variable
is set to be the same as the data type of `<expression>`. When a transient
variable is being re-assigned, the data type of `<expression>` must be
compatible with the data type of `<variable>`.

======================  ========================  ============================================
`<variable>` Data Type  `<expression>` Data Type  Note
======================  ========================  ============================================
boolean                 boolean
integer                 integer
real                    real
integer                 real                      Truncates all digits after the decimal point
real                    integer
string                  string
inst_ref<Object>        inst_ref<Object>
inst_ref_set<Object>    inst_ref_set<Object>
frag_ref                frag_ref
======================  ========================  ============================================

If `<variable>` is of data type `inst_ref<Object>`, `inst_ref_set<Object>`, or
`frag_ref<Object>`, then `<expression>` may be one of the following:

* Transient Variable
  
* Fragment Attribute

**Examples**

.. code-block:: pyrsl

   .assign obj_inst = prev_obj_inst
   .assign obj_set = next_obj_set
   .assign attr_inst = base_attr_frag.base_attr_inst
   .assign data_type_frag = attr_data_type_frag

   
Test Control Statements
-----------------------

Tests are supported through the use of the `if` statement:

.. code-block:: none

   .if (<condition>)
      <stmt_blck>
   [.elif (<condition>)
       <stmt_blck>]
   [.else
       <stmt_blck>]
   .end if
      
where `<condition>` is an expression with boolean result. `<stmt_blck>` is a
block of rule language statements. Several `elif` constructs may be present in
the same `if` construct.

**Examples**

.. code-block:: pyrsl

   .// example 1
   .if (class_inst.Numb < 100)
      literal text...
   .elif ((class_inst.Numb >= 200) && (class_inst.Numb < 300))
      literal text...
   .else
      literal text...
   .end if
       
   .// example 2
   .if ("${class_inst.Descrip:PERSISTENCE}" == "TRUE")
      source code for persistent classes ...
   .elif ("${class_inst.Descrip:PERSISTENCE}" == "FALSE")
      source code for non-persistent classes ...
   .else
     .print "Error in specification of persistence"
     .print " Class `${class_inst.Name}'"
     .exit 1
   .end if
   
   .// example 3
   .if ( p_operator == "NOT" )
     .assign cond = "!${p_operand_rval.rval}"
     .assign type = "boolean"
   .elif ( p_operator == "EMPTY" )
     .if ( p_operand_rval.var_card == "ONE" )
       .assign cond = "((${p_operand_rval.var_name} == 0) ? true : false)"
     .else
       .invoke method = GetCollectionIsEmptyMethodName()
       .assign cond = "${p_operand_rval.var_name}.${method.result}()"
     .end if
     .assign type = "boolean"
   .elif ( p_operator == "NOT_EMPTY" )
     .if ( p_operand_rval.var_card == "ONE" )
       .assign cond = "((${p_operand_rval.var_name} != 0) ? true : false)"
     .else
       .invoke method = GetCollectionIsEmptyMethodName()
       .assign cond = "!${p_operand_rval.var_name}.${method.result}()"
     .end if
     .assign type = "boolean"
   .else 
     .// Should never happen
     .print "TRANSLATOR ERROR: Unknown 'rval_unary_op' operator: ${p_operator}"
     .exit 100
   .end if

Function Control Statements
---------------------------
Functions are supported in the language to allow reuse of blocks of language
statements. Functions always return a fragment. A fragment can be thought of as
a pseudo-instance that has at least one, and possibly more attributes containing
data specified by the function. The intent of functions is to use them to build
fragments which can be organized into larger fragments and eventually used to
build a whole generated file.

To define a function, use the `function` statement:

.. code-block:: none

   .function <function_name>
      [.param <param_type> <param_name>
       .param <param_type> <param_name>
      ...]
      [<stmt_blck>]
   .end function    

where `<function_name>` is the name of the function. The name of the function
should be unique within the rule file, or any included rule files. `<param_type>`
is the type of the parameter. Allowed types are:

==============  ======================================
Parameter Type  Actual Parameter Forms Allowed
==============  ======================================
boolean         Rvalue of type boolean
integer         Rvalue of type integer
real            Rvalue of type real
string          Rvalue of type string
inst_ref        `<transient_var>` of type inst_ref
inst_ref_set    `<transient_var>` of type inst_set_ref
frag_ref        `<transient_var>` of type frag_ref 
==============  ======================================

To invoke a function, use the `invoke` statement:

.. code-block:: none
		
   .invoke [ <frag_ref_var> =] <function_name> (<actual_param>, <actual_param>...)

where `<frag_ref_var>` is a transient variable which holds a reference to the
fragment. `<function_name>` is the name of the function being invoked.
`<actual_param>` is an actual parameter.

The language define a set of predefined functions.

=========================================  ==========================================
Function Signature                         Description
=========================================  ==========================================
get_env_var(name: string)                  Get the value of an environmental variable
put_env_var(name: string, value: string)   Set the value of an environmental variable
shell_command(command: string)             Execute a shell command
file_read(filename: string)                Read text of a file
file_writefilename: string, text: string)  Write test to a file
string_to_integer(value: string)           Convert a string to an integer
string_to_real(value: string)              Convert at string to a real
integer_to_string(value: integer)          Convert an integer to a string
real_to_string(value: real)                Convert a real to a stirng
boolean_to_string(value: boolean)          Convert a boolean to a string
=========================================  ==========================================

Fragment Attributes
-------------------

Attributes may be defined for a fragment when the fragment is formed inside the
function. The attribute body is always defined. After the invocation of a
function, the body attribute contains the literal text lines within the function.

Additional attributes are defined by declaring transient variables inside the
function of the form:

.. code-block:: pyrsl

   .assign attr_<attribute_name> = <expression>

where `<attribute_name>` is the name of the attribute. The name of the attribute
should be selected to convey meaning to the caller of the function.

For example:

.. code-block:: pyrsl

   .function GetAttributeData
       .param inst_ref p_attr
       .assign attr_used = TRUE
       .assign attr_type = ""
       .if ( not p_attr.Used )
           .assign attr_used = FALSE )     
       .else
           .assign attr_type = "${p_attr.CppImplementationType}"
           // $(p_attr.Name}
       .end if
   .end function

specifies a function, that when called, results in the variables `type`, `used`,
and `body` being available on the call site through
`<frag_reg_var>.<attribute_name>`:

.. code-block:: pyrsl

   .select many attrs from instances of O_ATTR
   .for each attr in attrs
       .invoke attribute_data = GetAttributeData(attr)
       .if (attribute_data.used)
           ${attribute_data.body}
           ${attribute_data.type} ${attr.Name};
       .end if
   .end for

.. note::
   Be careful to make sure the `attr_<attribute_name>` variables are in scope
   when the `end function` statement is reached. For example:

   .. code-block:: pyrsl

      .function GetNewValueForValue
          .param integer p_value
          .if (p_value < 100)
              .assign attr_new_value = 22
          .else
              .assign attr_new_value = 2000
          .end if
      .end function

   results in the transient variable `attr_new_value` **not** becoming a
   fragment attribute since it falls out of scope with the `if` statement and is
   therefore not on the stack when the `end function` statement is encountered.

   A correct solution is:

   .. code-block:: pyrsl

      .function GetNewValueForValue
          .param integer p_value
          .assign attr_new_value = 0
          .if (p_value < 100)
              .assign attr_new_value = 22
          .else
              .assign attr_new_value = 2000
          .end if
      .end function

File Control Statements
-----------------------
File control statements are used to produce files based on the text accumulated
in the buffer when the statement is reached.

Emitting Text
^^^^^^^^^^^^^
All literal text is buffered as it is encountered in the rules. To output the
contents of the buffer to a file, use:

.. code-block:: pyrsl
		
   .emit to file <file_name>

where `<file_name>` the filename represeneted by a string. The `emit` statement
also clears the buffer's contents.

For example:

.. code-block:: pyrsl
		
   .emit to file "/source_code/$_{ss_inst.name}/$_{class_inst.name}.cpp"

results in a file being emitted in a directory based on the subsystem name with
a filename based on the class name.

If an emitted file already exists, then the contents of the new file are compared
to the existing file. If the files are the same, then the existing file is left
undisturbed, so that modification times are left in-tact. If the files are
different, then the existing file is replaced with the newly generated file.

To clear the contents of the buffer without emitting the contents to a file, use
the following statement:

.. code-block:: pyrsl

   .clear

Comments
^^^^^^^^
To add a comment in a rule file, use the following statement:

.. code-block:: pyrsl

   .comment <user_comment>

or

.. code-block:: pyrsl

    .// <user_comment>

At least one white space character must follow the .comment keyword. A white
space character does not need to follow the `.//` keyword.

All text from the comment keyword to the end of the line is ignored.

Include
^^^^^^^
To include another rule file, use the following statement:

.. code-block:: pyrsl

   .include <file_name>

where `<file_name>` is the filename represented by a string.

When a file is included, a marker is placed on the stack and the interpreter
begins interpretation on the first line of the included file. When all lines in
the included file have been processed, all variables pushed on the stack since
the include marker was pushed are considered out of scope (and therefore popped
from the stack). The interpreter then resumes interpretation on the line
following the `include` statement.

Handling Errors and Printing Information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To print a message to stderr from a rule, use the following statement:

.. code-block:: pyrsl

   .print <error_message>

where `<error_message>` is a string.

To stop the interpreter with integer value <exit_status> , use the following:

.. code-block:: pyrsl
		
   .exit <exit_status>

where `<exit_status>` is an integer.

Rvalues
-------
An rvalue is a specification of a literal value or the specification of a
variable.

Literals as Rvalues
^^^^^^^^^^^^^^^^^^^
Literal values can be entered for the each of the core data types. The table
below uses example specifications to illustrate how the literal values are
specified for each.

====================  ==============================
Core Data Type        Literal Specification Examples
====================  ==============================
boolean               true, false
integer               0, 256, -1
real                  0.0, 256.44
string                "Hello world"
inst_ref<Object>      N/A
inst_ref_set<Object>  N/A
frag_ref              N/A
====================  ==============================

Quoted Strings
^^^^^^^^^^^^^^
Quoted strings get special handling in the rule language. Each quoted string
is treated as a literal text line and is run through the variable substituter.
For example:

.. code-block:: pyrsl

   .assign name = class_inst.Name

and

.. code-block:: pyrsl
		
   .assign name = "${class_inst.Name}"
       
are equivalent. Treating quoted strings as literal text adds flexibility in
concisely specifying the string value. For example, the following shows
substitution variables used in the `if` statement and `emit` statement:

.. code-block:: pyrsl
		
   .select many class_set from instances of O_OBJ
   .for each class_inst in class_set
       .if ("${class_inst.descrip:PERSISTENCE}" == "TRUE")
           // Persistent implementation for class `${class_inst.Name}'
       .end if
       .emit to file "$_{class_inst.key_lett}.cpp"
   .end for    

Since the quoted strings get run through the literal text substituter, use $$ to
yield one $ character. In addition, use "" to yield one " character.

Variables as Rvalues
^^^^^^^^^^^^^^^^^^^^
Variables of the following types may be used as values:

* `<transient_variable>` of type boolean, integer, real, or string

* `<inst_ref_var>.<attribute>` where `<attribute>` is of type boolean, integer,
  real, or string

* `<frag_ref_var>.<attribute>` where `<attribute>` is of type boolean, integer,
  real, or string.
    
Expressions
-----------
The rule language supports simple and compound expressions.

Simple Expressions
^^^^^^^^^^^^^^^^^^
Simple expressions are single unary or binary operations:

.. code-block:: none
		
   (<unary_operator> <operand>)
   (<operand> <binary_operator> <operand>)

where `<unary_operator>` is a unary operator and `<binary_operator>` is a
binary operator. `<operand>` is the operand, e.g., a literal value, class
attribute, or transient variable.

**Examples**

.. code-block:: pyrsl

   .if (empty class_inst)
       .assign number_selected = cardinality class_set
   .end if
   .if (class_inst.Numb >= 100)
       .assign attr_decl = "${attr_inst.Type} $cr{attr_inst.name};"
   .end if

Compound Expressions
^^^^^^^^^^^^^^^^^^^^
Simple expressions can be combined to form a compound expressions:

.. code-block:: none

    (<unary_operator> <expression>)
    (<expression> <binary_operator> <operand>)
    (<operand> <binary_operator> <expression>)
    (<expression> <binary_operator> <expression>)

where `<unary_operator>` is a unary operator, `<binary_operator>` is a binary
operator. `<operand>` is an operand, e.g, a literal value, class attribute, or
transient variable. `<expression>` is an either a simple or compound expression.

Note the required use of the and operator to delimit expressions in a compound
expression. This takes away the issues surrounding precedence and associativity
of operators.

**Examples**

.. code-block:: pyrsl
		
   .invoke allocation_strategy = GetAllocationStrategyForClass( class )
   .if ( ( allocation_strategy.FixedBlock ) AND ( class.IsLocal ) )
       .select any fixed_block_unit from instances of MA_FBU where ( ( "${selected.Type}" == "LocalAllocationType1") OR ("${selected.Type}" == "LocalAllocationType2"))
   .end if

Operations
^^^^^^^^^^
The following tables define the core unary, binary, and set operators.

==============  ========================================================================
Unary Operator  Description
==============  ========================================================================
`not`           Logical Negation
`empty`         `inst_ref<Object>` or `inst_ref_set<Object>` test for empty set
`not_empty`     `inst_ref<Object>` or `inst_ref_set<Object>` test for not empty set
`first`         Test if the `inst_ref_set<Object>` cursor is on the first in the set
`not_first`     Test if the `inst_ref_set<Object>` cursor is not on the first in the set
`last`          Test if the `inst_ref_set<Object>` cursor is on the last in the set
`not_last`      Test if the `inst_ref_set<Object>` cursor is not on the last in the set
`cardinality`   Count the number of items in `inst_ref_set<Object>`
==============  ========================================================================

===============	 ==============================================================
Binary Operator
===============	 ==============================================================
`and`            logical AND
`or`             logical inclusive OR
`+`              arithmetic addition (integer & real) or concatenation (string)
`-`              arithmetic subtraction
`*`              arithmetic multiplication
`/`              quotient from arithmetic division
`%`              remainder from arithmetic division
`<`              less-than
`<=`             less-than or equal-to
`=`              equal-to
`!=`             not-equal-to
`>=`             greater-than or equal-to
`>`              greater-than
===============	 ==============================================================


Substitution Variables
----------------------
Literal text lines can contain substitution variables which allow you to pull
information out of the mode. and place it in a buffer so it can be emitted to
text files. A substitution variable takes on the following form:


.. code-block:: pyrsl

   $<format>{<inst_ref_var>.<attribute>:<parse_keyword>}

or


.. code-block:: pyrsl

   $<format>{<inst_chain>.<attribute>:<parse_keyword>}

or

.. code-block:: pyrsl

   $<format>{<frag_ref_var>.<attribute>}

or

.. code-block:: pyrsl

   $<format>{<transient_var>}

where

`<format>` are string substitution format characters that specify how to format
the string.

`<inst_ref_var>` is a reference to an instance in the model.

`<inst_chain>` is an instance chain which results in one instance.

`<frag_ref_var>` is a reference to a fragment which has been returned from a
function.

`<attribute>` is an attribute of the class referred to by `<inst_ref_var>` or
attribute of the fragment referred to by `<frag_ref_var>`.

`<parse_keyword>` represents a keyword which is parsed to obtain data from the
string on which the substitution occurs. See `Parse Keyword`_.

`<transient_var>` is a transient variable.

**Examples**

.. code-block:: pyrsl
		
   ${class_inst.Name}
   $_{ss_inst.Name}
   ${dt_inst.Descrip:TYPE}
   ${attr_inst->O_OBJ[R102].Key_Lett}
   $_{rattr_inst->O_BATTR[R113]->O_ATTR[R106].Name}

Substitution Variable Format Characters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The `<format>` characters are needed to allow the legal names in models to be
transformed into legal names in the generated file. For example, spaces are
allowed in class names in models but are not allowed in class names in C++. If
the class name from the model is going to be used as the class name in a
generated C++ file, then the class name must be transformed into a legal C++
name.

================  ================================================================
Format Character  Format Action
================  ================================================================
u                 Upper - make all characters upper case
c                 Capitalize - make the first character of each word capitalized
                  and all other characters of a word lower case
l                 Lower - make all characters lower case
_                 Underscore - change all white space characters to underscore
                  characters
r                 Remove - remove all white space. **Note**: The removal of
                  white space occurs after the capitalization has taken place in
		  the case of the CR or RC combination.
o                 cOrba - make the first word all lower case, make the first
                  character of each following word capitalized and all other
		  characters of the words lower case. Characters other than a-Z
		  a-z 0-9 are ignored.
t                 Translate - default user supplied translate format function.
                  No translation is made.
tnosplat          Built-in translate format function that removes \*'s (splats).
                  This can be used to remove the \* character found on polymorphic
		  events expressed in the BridgePoint metamodel.
t<switch>         User-defined translate format function defined by `<switch>`.
                  The user may define any number of custom translation formatters.
================  ================================================================

**Examples**

====================  ===========  ==============
Input                 Format       Output
====================  ===========  ==============
`Example Text`        `u`          `EXAMPLE TEXT`
`Example Text`        `u_`         `EXAMPLE_TEXT`
`Example Text`        `ur`         `EXAMPLETEXT`
`ExamplE TExt`        `c`          `Example Text`
`ExamplE TExt`        `c_`         `Example_Text`
`ExamplE TExt`        `cr`         `ExampleText`
`ExamplE TExt`        `l`          `example text`
`ExamplE TExt`        `l_`         `example_text`
`ExamplE TExt`        `lr`         `exampletext`
`ExamplE@34 TExt`     `o`          `example34Text`
`* ExamplE TExt *`    `_tnosplat`  `Example_Text`
====================  ===========  ==============

Translate Format Character
^^^^^^^^^^^^^^^^^^^^^^^^^^
The $t format character allows the user to execute custom string transformations
hat are not supplied by the interpreter. For example, most computer languages
only allow ASCII to be used for program source text; if a model contains
(non-ASCII) international characters, a user-supplied translate function could
be added to change these strings to an ASCII string that can be used by the
language compiler.

When specifying multiple `<format>` characters, the $t character must be the
last. All characters between the `t` and the `{` are assumed to be part of the
`<switch>` used by the $t format. The $t substitution is applied before any
other substitution (i.e., $ut{...} applies $t first, then $u ). The default
translate function when nothing is supplied by the user returns the string
unchanged. The supplied translate function also ignores all `<switch>` 's except
nosplat.

The following example demonstrate how this may be acchived in pyrsl:

.. code-block:: python

   from rsl import gen_erate
   from rsl import bridge
   from rsl import string_formatter

   @string_formatter('trmquot')
   def remove_quot(s):
       QUOTES = "'\""
       first_index = 0
       last_index = len(s) - 1
    
       if s[0] in QUOTES:
           first_index += 1

       if s[-1] in QUOTES:
           last_index +- 1

       return s[first_index:last_index]


   print('Running my custom version of gen_erate')
   rc = gen_erate.main()
   sys.exit(rc)

The following example demonstrate how to use this new translation function

.. code-block:: pyrsl

   .assign s = "'hello world'"
   .print "$trmquot{s}"

Parse Keyword
^^^^^^^^^^^^^
A parse keyword is a piece of text placed in a string attribute of a class (such
as a description) in the model. Rules may gain access to the string that follows
the parse keyword, up to the next newline character, by using substitution
variables of the following type:

.. code-block:: pyrsl

   $format{<inst_ref_var>.<attribute>:<parse-keyword>}

.. code-block:: pyrsl

   $format{<inst_chain>.<attribute>:<parse-keyword>}

For example, if an attribute description contains the following text and two
parse keywords:

.. code-block:: none

   This attribute captures the name of the quick brown fox who jumped over the
   lazy brown dog.
   
      TYPE: String
      LENGTH: 64

the data after TYPE: can be assigned to attr_type by using the following
substitution:

.. code-block:: pyrsl

   .assign attr_type = "${attr_inst.Descrip:TYPE}"

The data after LENGTH: can be obtained with the following substitution:

.. code-block:: pyrsl

   .assign attr_length = ${attr_inst.Descrip:LENGTH}

.. note:: The above examples explicitly place architectural information into the
	  application model. This has ramifications on the reusability of the
	  models across different application-independent system architectures.
	  Use with care!

Information Substitution Variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
There are some special substitution variables available which can be used
anywhere:

.. code-block:: pyrsl

   ${info.date}
   ${info.user_id}
   ${info.arch_file_name}
   ${info.arch_file_line}
   ${info.interpreter_version}
   ${info.interpreter_platform}
   ${info.unique_num}

The word info is a keyword and cannot be used as a transient variable name.
The first six are commonly used for information placed in the headers of
generated files. The last is used to produce unique variable names within the
generated code.

`${info.date}` returns the current date and timestamp.

`${info.user_id}` returns the user id of the user running pt_gen_file .

`${info.arch_file_name}` returns the name of the rule file currently being
executed.

`${info.arch_file_line}` returns the current line number in the rule file.

`${info.interpreter_version}` returns the version of pt_gen_file .

`${info.interpreter_platform}` returns the platform on which pt_gen_file is
running.

`${info.unique_num}` returns a unique integer each time it is referenced. For
example, the first time it is referenced, it may produce 1, the next time 2,
the next time 3, and so on. The order of the unique numbers generated is
guaranteed to be exactly the same from one invocation of the interpret to the
next.




