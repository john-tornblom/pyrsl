Language Reference
##################

The Rule Specification Language (RSL) is a language that operates in two modes.
One mode where lines of text encountered at input are staged onto a buffer (the
buffer mode), and one mode that controls the buffer (the control mode). When
operating in one mode, the other mode is inactive. The buffer mode is active by
default. If the buffer mode encounters a line with the dot character (.) as the
first non-whitespace character, the control mode is activated. When the control
mode encounters a line break, the buffer mode is turned back on. The program
terminates when all input has been processed.

The following sections describe how the language works when operating in the
control mode. For more information on the buffer mode, see `Buffer Mode`_.

.. note::
   Keywords and names are case **insensitive**. Names can be made up of any
   alpha (a-z, A-Z) or numeric (0-9) characters or underscore (_) character.
   Names cannot begin with a numeric character, and cannot conflict with
   keywords.

Basic Constructs
================
The following sections describe basic language constructs that share
similarities with other general purposed programming languages.

Core Types
----------
The RSL language define five core types; *boolean*, *integer*, *real*, *string*,
and *unique_id*. The *boolean* type is limited to two values (*true* and
*false*), whereas the other core types are unbounded. In practice however, all
types are bounded. The exact ranges depend on the implementation. Generally,
integers are represented by signed 64bit integers, reals by 64bit floating point
numbers, unique_ids by 128bit unsigned integers, and strings are bounded by the
amount of available RAM.

.. note:: There are additional types that are used to hold references to
	  *instances* and *fragments*. These types are further explained in
	  `Model Interactions`_ and `Functions and Fragments`_.

Literal Values
--------------
Literal values can be entered for four of the core types. The table below
exemplifies how these literal values are specified for each core type.

====================  ==============================
Core Type             Examples (separated by ,)
====================  ==============================
boolean               true, false
integer               0, 256, -1
real                  0.0, -256.44
string                "Hello world"
====================  ==============================

.. tip::
   Values of the core type unique_id can be created by reading the global
   information fragment attribute *unique_num*. See `Global Information
   Fragment`_ for more information.

Transient Variables
-------------------
All transient variables are implicitly declared upon the first assignment.
Assignments are expressed using the *assign* keyword as exemplified below:

.. code-block:: pyrsl

   .assign My_Boolean = true
   .assign My_Integer = 42
   .assign My_Real    = 3.14
   .assign My_String  = "Hello world!"

Any subsequent assignment simply re-assign the same variable. A re-assignment
of a variable to a different type is not allowed. A stack execution model is
assumed. Variables are pushed onto the stack as they are implicitly declared
and are popped off the stack as they fall out of scope. Any variable implicitly
declared inside of a block falls out of scope when the end of the block is
encountered.

Comments
--------
Comments can be entered using the *comment* statement as exemplified below:

.. code-block:: pyrsl

   .comment My comment

A shorter variant inspired by C-like languages is also available:

.. code-block:: pyrsl

    .//My other comment

At least one whitespace character must follow the *comment* keyword. A
whitespace character does not need to follow the shorter variant. 

Expressions
-----------
Variables and values can be combined into expressions using operators. There are
three kinds of expressions; *unary*, *binary*, and *compound* expressions. The
following sections present operators that are valid for core types.

.. note:: There are additional operators available that are not valid for core
	  types These operators are further explained in `Instances and Sets`_
	  and `Iterating Sets of Instances`_

Unary expressions
^^^^^^^^^^^^^^^^^
Unary expressions consist of one operator and one operand. Below is a table of
unary operators that are valid for core types.

+----------------+---------------+------------------+
| Unary Operator | Core Type(s)  | Description      |
+================+===============+==================+
| not            | any           | Logical negation |
+----------------+---------------+------------------+
| \-             | integer, real | Numeric negation |
+----------------+---------------+------------------+

The following example demonstrates how to perform a numeric negation on an
integer:

.. code-block:: pyrsl

    .assign Positive_Integer = 42
    .assign Negative_Integer = -Positive_Integer

Binary expressions
^^^^^^^^^^^^^^^^^^
Binary expressions consist of one operator and two operands. Below is a table of
binary operators valid for core types.

+-----------------+--------------------------------------+
| Binary Operator | Description                          |
+=================+======================================+
| and             | logical AND                          |
+-----------------+--------------------------------------+
| or              | logical inclusive OR                 |
+-----------------+--------------------------------------+
| \+              | arithmetic addition (integer & real) |
|                 | or concatenation (string)            |
+-----------------+--------------------------------------+
| \-              | arithmetic subtraction               |
+-----------------+--------------------------------------+
| \*              | arithmetic multiplication            |
+-----------------+--------------------------------------+
| /               | quotient from arithmetic division    |
+-----------------+--------------------------------------+
| %               | remainder from arithmetic division   |
+-----------------+--------------------------------------+
| <               | less-than                            |
+-----------------+--------------------------------------+
| <=              | less-than or equal-to                |
+-----------------+--------------------------------------+
| =               | equal-to                             |
+-----------------+--------------------------------------+
| !=              | not-equal-to                         |
+-----------------+--------------------------------------+
| >=              | greater-than or equal-to             |
+-----------------+--------------------------------------+
| >               | greater-than                         |
+-----------------+--------------------------------------+

The following example demonstrates how to perform a numeric addition of two
integers, concatenation of two strings, and a greater-than comparison between
two integers:

.. code-block:: pyrsl

    .assign My_Addition = 42 + 5
    .assign My_Concatenation = "Hello " + "world"
    .assign My_Comparison = 5 > My_Addition
    


Compound expressions
^^^^^^^^^^^^^^^^^^^^
Compound expressions consist of several operators and operands that are combined
using matching parentheses that determine precedence. The following example
demonstrate a series of string concatenations.

.. code-block:: pyrsl

    .assign My_String = ("Hello" + (" " + "world"))

In the example above, *" "* and *"world"* are concatenated first. Then,
*"Hello"* and *" world"* are concatenated.

If, Elif and Else
-----------------
The keywords *if*, *elif* and *else* can be combined to form a statement that
control execution of other statements based on the outcome of boolean
expressions. The following example demonstrate one way on how the three keywords
may be combined.

.. code-block:: pyrsl

    .if (My_Control_Variable > 0)
        .// Do something
    .elif (My_Control_Variable < 0)
        .// Do something else
    .else
        .// Do nothing
    .end if

.. hint:: 
   Any number of *elif* constructs may be present in the same statement, and the
   *else* construct is optional.

While Loops
-----------
The *while* statement provides a general purpose iteration mechanism. The
following example demonstrates how to compute the sum of all integers between
one and ten.

.. code-block:: pyrsl

    .assign Sum = 0
    .assign Counter = 0
    .while (Counter < 10)
        .assign Counter = Counter + 1
        .assign Sum = Sum + Counter
    .end while

The *break while* statement provide an alternative technique to end iterations.
When executed, the *break while* statement causes control to be transferred to
the statement after the *end while* statement corresponding to the innermost
executing *while* loop. The following example performs the same computation as
the previous example presented above, but using the *break while* statement to
halt iteration.
   
.. code-block:: pyrsl

    .assign Sum = 0
    .assign Counter = 0
    .while (true)
        .if(Counter < 10
            .assign Counter = Counter + 1
            .assign Sum = Sum + Counter
	.else
	    .break while
	.end if
    .end while

Quoted Strings
--------------
Quoted strings get special handling in the language. Each quoted string is
treated as a literal text line and is run through a variable substituter
discussed in `Substitution Variables`_. This allows simple string concatenation
without using binary expressions. The following example concatenates the
variables *x* and *y* with a whitespace between them.

.. code-block:: pyrsl
		
    .assign x = "Hello"
    .assign y = "world"
    .assign s = "${x} ${y}"

.. note:: Since quoted strings get run through a literal text substituter, use
	  $$ to yield one $ character. In addition, use "" to yield one "
	  character. See `Substitution Variables`_ for more information.
    
Terminal Logging
----------------
The *print* statement can be used to print string literals to the standard
output.

.. code-block:: pyrsl

    .print "Hello world"

Since the print statement only accept string literals, variables must be quoted
before being printed. The following example prints the number 42 to standard
output.

.. code-block:: pyrsl

    .assign My_Integer = 42
    .print "${My_Integer}"

Program Termination
-------------------
The *exit* statement can be used to terminate a program. Optionally, an integer
based exit code may also be provided. For example:

.. code-block:: pyrsl

    .exit 1

Model Interactions
==================
The following sections describe language features that allow interaction with an
xtUML model. Below is a class diagram that examples in the following sections
use.

.. code-block:: none
		
    -----------------                             ----------------------
   | Class     {CLS} |                           | Other Class  {O_CLS} | prev
   |------------------ *         R1        0.. 1 |----------------------|------
   | Number: integer |---------------------------| Name: string         | 0..1 |
    -----------------             |               ----------------------       |
                                  |                           0..1 | next   R2 |
                         ---------------------                      -----------
                        | Assoc Class {A_CLS} |
                        |---------------------|
                        | My_Boolean: boolean |
                         ---------------------

There are three classes in the example above; *Class*, *Other Class*, and *Assoc
Class*. The text in the upper right corner within curly brackets on each class
is called a *key letter* and is used as the class identifier in RSL. The three
classes are associated to each other via the association *R1*. Furthermore,
there is a reflexive association *R2* on *Other Class*. Reflexive associations
require a phrase to distinguish the directions of the *links* (*next* and *prev*
in the example above). At the end of each link is the *cardinality*. The
cardinality specify how many instances may be connected to a link.

The *Assoc Class* is a special kind of class called an association class. Such
classes are used to add attributes to an association. The cardinality of links
to association classes are not explicitly stated, they are implicitly assumed to
be exactly one.

.. note::
   The BridgePoint editor allow its users to specify links to association
   classes with the cardinality 1..*. Such association classes are rarely used,
   and should be avoided. The same semantics may be obtained by introducing a
   new class associated with the association class.

Instances and Sets
------------------
The introduction of instances and links into the language also brings new types.
Specifically, the types *inst_ref* and *inst_ref_set*.

The type *inst_ref* acts as a reference to an instance of a class in the model,
and is used to access instance attributes. The following table lists unary
operators that are valid for transient variables of the type *inst_ref*.

+----------------+-------------------------------------------------------------+
| Unary Operator | Description                                                 |
+================+=============================================================+
| empty          | Check if the *inst_ref* operand refers to an instance       |
+----------------+-------------------------------------------------------------+
| not_empty      | Logical negation of the *empty* operator                    |
+----------------+-------------------------------------------------------------+
| cardinality    | Count the number of instances the *inst_ref* operand refers |
|                | to (zero or one)                                            |
+----------------+-------------------------------------------------------------+

The type *inst_ref_set* is used to holds references to several instances. The
following table lists unary operators that are valid for transient variables of
the type *inst_ref_set*.

+----------------+-------------------------------------------------------------+
| Unary Operator | Description                                                 |
+================+=============================================================+
| empty          | Check if the *inst_ref_set* operand contains any instance   |
|                | reference                                                   |
+----------------+-------------------------------------------------------------+
| not_empty      | Logical negation of the *empty* operator                    |
+----------------+-------------------------------------------------------------+
| cardinality    | Count the number of items the *inst_ref_set* operand refers |
|                | to                                                          |
+----------------+-------------------------------------------------------------+

There are also a number of binary operations that accept a mix of *inst_ref*
and *inst_ref_set* operands. When any of the operands are of the type
*inst_ref*, they are interpreted as an *inst_ref_set* that contains the referred
to instance.

+-----------------+-----------------------------------------------------------+
| Binary Operator | Description                                               |
+=================+===========================================================+
| \|              | Returns the union of both operands                        |
+-----------------+-----------------------------------------------------------+
| \&              | Returns the intersection between both operand             |
+-----------------+-----------------------------------------------------------+
| \-              | Returns a set of instance references that are in the left |
|                 | operand, but not in the right operand                     |
+-----------------+-----------------------------------------------------------+
| ==              | Check if the intersection between both operands is empty  |
+-----------------+-----------------------------------------------------------+
| !=              | Logical negation of ==                                    |
+-----------------+-----------------------------------------------------------+

.. note:: There are additional unary operators for sets that are only valid
	  during set iteration. See `Iterating Sets of Instances`_ for more
	  information.

Selecting Instances
-------------------
Instances may be selected from the model by using the key letter of the class.
The following example demonstrates how to select any arbitrary instance of the
class with the key letter *CLS*, and store a reference to the instance in a
variable named *inst*.

.. code-block:: pyrsl

    .select any inst from instances of CLS

It is also possible to select several instances of some class using the *many*
keyword instead of *any*. The following example selects all instances of *CLS*
and stores an instance set reference in a variable named *inst_set*.

.. code-block:: pyrsl

    .select many inst_set from instances of CLS

Accessing Class Attributes
--------------------------
Class attributes may be accessed using the *dot* operator (.). The following
example selects an arbitrary instance of *CLS*, and increment its *Number*
attribute by one.

.. code-block:: pyrsl

    .select any inst from instances of CLS
    .assign inst.Number = inst.Number + 1

Iterating Sets of Instances
---------------------------
The *for each* statement is used to iterate sets of instances. The following
example computes the sum of all *CLS.Number* attributes.

.. code-block:: pyrsl

    .assign Sum = 0
    .select many inst_set from instances of CLS
    .for each inst in inst_set
        .assign Sum = Sum + inst.Number
    .end for

During iteration, the following unary operators are supported.

+----------------+---------------------------------------------------------------+
| Unary Operator | Description                                                   |
+================+===============================================================+
| first          | Check if the *inst_ref_set* operand is on its first iteration |
+----------------+---------------------------------------------------------------+
| not_first      | Logical negation of *first*                                   |
+----------------+---------------------------------------------------------------+
| last           | Check if the *inst_ref_set* operand is on its last iteration  |
+----------------+---------------------------------------------------------------+
| not_last       | Logical negation of *last*                                    |
+----------------+---------------------------------------------------------------+

The following example demonstrates how to generate a comma-separated list of
*O_CLS* names.

.. code-block:: pyrsl

    .select many inst_set from instances of O_CLS
    .assign s = ""
    .for each inst in inst_set
        .assign s = s + inst.Name
        .if (not_last inst_set)
	    .assign s = s + ", "
	.end if
    .end for

    
Filtering Selections
--------------------
Instance selections can be filtered using the *where* keyword. The *selected*
keyword may be used inside a where-clause to access attributes on the instance
currently being selected. The following example demonstrates how to select
instances of *CLS* whose attribute *Number* is larger than 100.

.. code-block:: pyrsl

    .select many inst_set from instances of CLS where (selected.Number > 100)

Navigating Instances
--------------------
Associations between classes may be navigated using the *related by* keyword.
The *related by* form of the *select* statement uses an instance chain to
specify a path through the related instances. An instance chain is simply a
sequence of class key letter/association number pairs which specify the path
from the source instance to the destination class. The result of a select is
zero, one or more instances of the last class of the chain.

The following example selects an arbitrary instance of *CLS* and navigates
across *R1* to *O_CLS* via *A_CLS*.

.. code-block:: pyrsl

    .select any cls from instance of CLS
    .select one other_cls related by cls->A_CLS[R1]->O_CLS[R1]

.. tip::
   The previous navigation through the association *R1* was in two steps. First
   to the associative-link class and then to the other side of the association.
   Recent versions of the language allow navigation across association classes
   without explicitly going via the association class, e.g.

   .. code-block:: pyrsl

       .select any cls from instance of CLS
       .select one other_cls related by cls->O_CLS[R1]
   
To navigate across reflexive associations, a phrase indicating the direction
must be provided. For example:

.. code-block:: pyrsl

    .select any other_cls from instance of O_CLS
    .select one next related by other_cls->O_CLS[R2.'next']

.. warning::
   In recent versions of the language, the phrases you specify in reflexive
   navigations has been swapped to be in line with the Object Action Language
   (OAL) used in BridgePoint.

The handle from which a navigation starts in may be an instance reference set.
In such cases, each instance reference in the set is navigated automatically.
The following example selects all *CLS* instances that are connected to a
*O_CLS* across *R1*.

.. code-block:: pyrsl

    .select many assoc_set from instance of A_CLS
    .select many cls_set related by assoc_set->CLS[R1]

Creating Instances
------------------
The *create object instance* statement is used to create new instances of a
class. The following example creates an instance of *CLS* and assigns its
*Number* attribute to five.

.. code-block:: pyrsl

    .create object instance cls of CLS
    .assign cls.Number = 5

Connecting Instances
--------------------
Instances can be connected and disconnected across associations using the
*relate* and *unrelate* statements. The following example creates two instances
of *O_CLS* and connects them across the reflexive association *R2*.

.. code-block:: pyrsl

    .create object instance inst1 of O_CLS
    .create object instance inst2 of O_CLS
    .relate inst1 to inst2 across R1.'other'

The following example disconnects them again.

.. code-block:: pyrsl

    .unrelate inst1 from inst2 across R1.'other'

Recent versions of the language allow connecting and disconnecting association
classes in one single control statement. The following example creates one
instance of *CLS*, *O_CLS* and *A_CLS* and then connects them to each other.

.. code-block:: pyrsl

    .create object instance cls of CLS
    .create object instance other_cls of O_CLS
    .create object instance assoc_cls of A_CLS

    .relate cls to other_cls across R1 using assoc_cls

The following example disconnects them again, and deletes the association
instance.

.. code-block:: pyrsl

    .unrelate cls from other_cls across R1 using assoc_cls
    .delete object instance assoc_cls

.. note:: Disconnected instances of association classes violates model
	  integrity and must be deleted manually.
   
Deleting Instances
------------------
The *delete object instance* statement is used to delete instances from the
model. The following example selects an arbitrary instance of *CLS* and deletes
it.

.. code-block:: pyrsl

    .select any inst from instances of CLS
    .delete object instance inst

When an instance is deleted, the instance is removed from the class extent, and
is unrelated from existing associations. Note that it is up to the user to
ensure model integrity, e.g. that the data is not violating association
constraints.

.. warning::
   The *delete* statement **only** remove instances from the model, transient
   references may still refer to them. Depending on the language implementation,
   accessing such references may result in undefined behaviour. 

Functions and Fragments
=======================
Functions allow reuse of blocks of control statements. All functions return a
*fragment*. A fragment can be thought of as a pseudo-instance that has at least
one, and possibly more attributes containing data specified by the function.
The intent of functions is to use them to build fragments which can be organized
into larger fragments and eventually used to build a whole generated file.

.. note::
   All functions have their own literal buffer and cannot modify any other
   buffer when they operate in buffer mode.

Defining Functions
------------------
Functions are defined using the *function* statements, and parameters are
defined using the *param* statement. In addition to the core types, three
additional types can be used by parameters; *inst_ref*, *inst_ref_set* and
*frag_ref*. The following example define a function with one parameter of each
type.

.. code-block:: pyrsl

   .function
       .param boolean      My_Boolean
       .param integer      My_Integer
       .param real         My_Real
       .param unique_id    My_Unique_Id
       .param string       My_String
       .param inst_ref     My_Instance
       .param inst_ref_set My_Set
       .param frag_ref     My_Fragment
   .end function

.. tip::
   Recent versions of the language allow specifying the kind of class an
   *inst_ref* or *inst_ref_set* may refer to. The kind of class is specified
   using angle brackets as examplified below.

   .. code-block:: pyrsl

       .function Func
           .param inst_ref<Key_Letter>     My_Instance
           .param inst_ref_set<Key_Letter> My_Set
       .end function

   When the kind of class is specified for an *inst_ref* or *inst_ref_set*,
   arguments are type checked accordingly.
   
Defining Fragment Attributes
----------------------------
Attributes may be defined for a fragment when the fragment is formed inside the
function. The attribute *body* is always defined. After the invocation of a
function, the *body* attribute contains the literal text buffered within the
function while operating in buffer mode.

Additional attributes are defined by declaring transient variables inside the
function with a name that starts with *attr_*. The following example defines a
function name *Func* that return a fragment with two attributes; *body* and
*data*.

.. code-block:: pyrsl

   .function Func
       .assign attr_data = "My Data"
   .end function
   
.. note::
   Be careful to make sure the *attr_* variables are in scope when the *end
   function* statement is reached. Consider the following example.

   .. code-block:: pyrsl

      .function Func
          .param integer p_value
          .if (p_value < 100)
              .assign attr_data = "Some Data"
          .else
              .assign attr_data = "Some other data"
          .end if
      .end function

   The example above results in the transient variable *attr_data* **not**
   becoming a fragment attribute since it falls out of scope with the *if*
   statement, and is therefore not on the stack when the *end function*
   statement is encountered.

   A correct solution is the following:

   .. code-block:: pyrsl

      .function Func
          .param integer p_value
	  .assign attr_data = ""
          .if (p_value < 100)
              .assign attr_data = "Some Data"
          .else
              .assign attr_data = "Some other data"
          .end if
      .end function
      
Invoking Functions
------------------
Functions are invoked using the *invoke* statement. The following example
invokes a function named *Func* that takes an integer as parameter, then stores
the returned fragment into a transient variable named *Frag*.

.. code-block:: pyrsl
		
   .invoke Frag = Func(4)

.. tip:: The returning fragment may be omitted from the syntax as exemplified
	 below.
	 
	 .. code-block:: pyrsl
		
	     .invoke Func(4)

	 This may be useful when functions only modify the global scope, e.g.
	 when modifying instances or emitting files to disk.
   
Available Builtin Functions
---------------------------
The language define a set of builtin functions. The following two functions can
be used to read and modify environmental variables in the operating system.

.. code-block:: pyrsl

   .function get_env_var
       .param string name
   .end function

   .function put_env_var
       .param string name
       .param string value
   .end function

The following function can be used to invoke the operating system shell
with an arbitrary command.

.. code-block:: pyrsl

   .function shell_command
       .param string cmd
   .end function

The following two functions can be used to read and write files on disk.

.. code-block:: pyrsl

   .function file_read
       .param string filename
   .end function
   
   .function file_write
       .param string filename
       .param string text
   .end function

The following functions can be used to convert values of various core types.

.. code-block:: pyrsl

   .function string_to_integer
       .param string value
   .end function
   
   .function string_to_real
       .param string value
   .end function

   .function integer_to_string
       .param integer value
   .end function
   
   .function real_to_string
       .param real value
   .end function
   
   .function boolean_to_string
       .param boolean value
   .end function

Global Information Fragment
---------------------------
There is a special fragment named *info* that is always accessible.
The word *info* is thus a keyword and cannot be used to name a transient
variable.

The following table lists all attributes accessible from the *info* fragment.

+----------------------+-------------------------------------------------------+
| Attribute Name       | Description                                           |
+======================+=======================================================+
| date                 | current date and timestamp                            |
+----------------------+-------------------------------------------------------+
| user_id              | user id of the using running the program              |
+----------------------+-------------------------------------------------------+
| arch_file_name       | basename of the rule file currently being executed    |
+----------------------+-------------------------------------------------------+
| arch_file_line       | current line number of the executing file             |
+----------------------+-------------------------------------------------------+
| arch_file_path       | full path to the executing file                       |
+----------------------+-------------------------------------------------------+
| arch_folder_path     | full path to the folder containing the executing file |
+----------------------+-------------------------------------------------------+
| interpreter_version  | the name and version of the RSL interpreter           |
+----------------------+-------------------------------------------------------+
| interpreter_platform | the name of that platform on which the interpreter is |
|                      | running                                               |
+----------------------+-------------------------------------------------------+
| unique_num           | returns a unique_id each time it is accessed. For     |
|                      | example the first time it is referenced, it may       |
|                      | produce 1, the next time 2, the next time 3, and so   |
|                      | on. The order of the  unique numbers generated is     |
|                      | guaranteed to be exactly the same from one invocation |
|                      | of the program to the next.                           |
+----------------------+-------------------------------------------------------+

The following example creates a string that contains the current date and time.

.. code-block:: pyrsl

   .assign s = "Current date and time is: " + info.date

Including Files
===============
The *include* statement can be used to include files. The following example
includes a file named *my_file.inc*.

.. code-block:: pyrsl

   .include "my_file.inc"

When a file is included, a marker is placed on the stack and the execution
continues on the first line of the included file. When all lines in the included
file have been processed, all variables pushed onto the stack since the include
marker was pushed are considered out of scope (and therefore popped from the
stack). The execution then resumes on the line following the *include*
statement.

.. note:: Transient variables that are accessible just before a file is included
	  are also accessible from the within included file.

Emitting Buffered Text
======================
The *emit to file* statement can be used to output buffered text to disk.
The following example emits the buffer to a file named *emit_data.txt* into a
folder named *data* located in the current working directory.

.. code-block:: pyrsl
		
   .emit to file "data/emit_data.txt"

The *emit* statement also clears the buffer's contents.

If an emitted file already exists, the contents of the new file are compared
to the existing file. If the files are the same, then the existing file is left
undisturbed, so that modification times are left intact. If the files are
different, the existing file is replaced with the newly generated file.

.. note:: Folders leading up to the filename are created automatically.

To clear the contents of the buffer without emitting the contents to a file, the
*clear* statement can be used as exemplified below.

.. code-block:: pyrsl

   .clear

Buffer Mode
===========
The following sections describe how the language behave in the buffer mode.
Specifically, how to access variables defined in the control mode, how to
transform strings using formatters and parse keywords, and how to escape
special characters.

Substitution Variables
----------------------
Literal text lines can contain substitution variables which allow you to access
variables defined in the control mode and place its content in a buffer so it
can be emitted to text files. The following example define a transient variable
named *Data* in the control mode, and puts its value into the buffer surrounded
by the html tag *div*.

.. code-block:: pyrsl

    .assign Data = "Some text"
    <div>${Data}</div>

When emitted to a file, the above example would produce the following output.

.. code-block:: html

   <div>Some text</div>

Parse Keywords
--------------
A parse keyword is a piece of text placed in a string-based variable. Text that
follows the parse keyword, up to the next line break character, can be
extracted.

.. code-block:: pyrsl

    .assign Data = "VALUE: Hello world"
    ${Data:VALUE}

The example above produce the literal text *Hello world*.

Navigating Associations
-----------------------
The buffer mode supports navigation across one-to-one associations to access
attributes. The following example demonstrates how to navigate from an instance
of *CLS* across the association *R1* to access the attribute *Name* on the class
*O_CLS*.

.. code-block:: pyrsl

    .assign select any cls from instances of CLS
    ${cls->O_CLS[R1].Name}

Transforming Substitution Variables
-----------------------------------
Values held by a substitution variable can be transformed by a number of pre-
defined format characters, e.g. converting all characters to upper-cased
letters (the character *u*), or replacing whitespaces with underscore (using
the underscore character).

.. code-block:: pyrsl

    .assign Data = "Some text"
    <div>$u_{Data}</div>

When the example above is executed, the following literal text is produced.

.. code-block:: html

   <div>SOME_TEXT</div>

The table below list all pre-defined format characters available in the
language.

+------------------+-----------------------------------------------------------+
| Format Character | Transformation Function                                   |
+==================+===========================================================+
| u                | Upper - make all characters upper case                    |
+------------------+-----------------------------------------------------------+
| c                | Capitalize - make the first character of each word        |
|                  | capitalized and all other characters of a word lowercase  |
+------------------+-----------------------------------------------------------+
| l                | Lower - make all characters lowercase                     |
+------------------+-----------------------------------------------------------+
| _                | Underscore - change all whitespace characters to          |
|                  | underscore characters                                     |
+------------------+-----------------------------------------------------------+
| r                | Remove - remove all whitespace. **Note**: The removal of  |
|                  | whitespace occurs after the capitalization has taken      |
|                  | place in the case of the CR or RC combination.            |
+------------------+-----------------------------------------------------------+
| o                | cOrba - make the first word all lowercase, make the first |
|                  | first character of each following word capitalized and    |
|                  | all other characters of the words lowercase. Characters   |
|                  | other than a-Z a-z 0-9 are ignored.                       |
+------------------+-----------------------------------------------------------+

The following table lists example input and output for various combinations of
pre-defined format characters.

+------------------+--------+---------------+
| Input            | Format | Output        |
+==================+========+===============+
| Example Text     | u      | EXAMPLE TEXT  |
+------------------+--------+---------------+
| Example Text     | u\_    | EXAMPLE_TEXT  |
+------------------+--------+---------------+
| Example Text     | ur     | EXAMPLETEXT   |
+------------------+--------+---------------+
| ExamplE TExt     | c      | Example Text  |
+------------------+--------+---------------+
| ExamplE TExt     | c\_    | Example_Text  |
+------------------+--------+---------------+
| ExamplE TExt     | cr     | ExampleText   |
+------------------+--------+---------------+
| ExamplE TExt     | l      | example text  |
+------------------+--------+---------------+
| ExamplE TExt     | l\_    | example_text  |
+------------------+--------+---------------+
| ExamplE TExt     | lr     | exampletext   |
+------------------+--------+---------------+
| ExamplE\@34 TExt | o      | example34Text |
+------------------+--------+---------------+

Defining Custom Format Characters
---------------------------------
It is possible for a user to define its own custom format characters. These
format characters must start with the letter *t*. When using multiple format
characters at the same time, the user-defined format character must be specified
last. User-defined format characters are applied before any other pre-defined
format characters (i.e., $ut{...} applies *t* first, then *u*). The default
transformation function when nothing is supplied by the user leaves the string
unchanged.

The following example demonstrate how to define a new format character in pyrsl
that remove quotes from strings.

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

The following example demonstrate how to use the format character defined above.

.. code-block:: pyrsl

   .assign s = "'hello world'"
   $trmquot{s}

When the example above is executed, the value of *s* is transformed from *'hello
world'* into *hello world*.

Escaping Special Characters
---------------------------
A literal text line with the dot dot character sequence (..) as the first
non-whitespace characters results in the dot character being emitted. A dot
character anywhere else in the literal text line results in a dot character
being emitted (i.e. no special treatment).

The dollar character ($) is used by the buffer mode to access variables defined
in the control mode. Consequently, to stage a dollar character onto the buffer,
the character sequence $$ shall be used.

Newline characters at the end of a line of literal text are passed through to
the emitted output. If you do not want a newline at the end of an emitted line
(presumably due to control statement constraints), then place a backslash
character (\\) as the last character of the literal text line. The `\\\\`
character sequence as the last two characters of the literal text line results
in one backslash character and one newline character as the last characters of
an emitted line. The `\\\\\\` character sequence as the last three characters of
a line of literal text results in one backslash character as the last character
of an emitted line with no newline character.

The following table summerize the escaping rules presented above.

+-------------------------+----------------------+-------------------------+
| Character               | Position             | To Generate at Position |
+=========================+======================+=========================+
| .                       | First non-whitespace | ``..``                  |
+-------------------------+----------------------+-------------------------+
| $                       | Any                  | ``$$``                  |
+-------------------------+----------------------+-------------------------+
| \\ (with new line)      | Last                 | ``\\``                  |
+-------------------------+----------------------+-------------------------+
| \\ (without new line)   | Last                 | ``\\\``                 |
+-------------------------+----------------------+-------------------------+
