*** Variables ***
@{rc}             5
@{x}              5
@{y}              5

*** Test Cases ***
Test__BuiltIn__01
    Run Keyword If    os.sep == '/'    Log    Not on Windows
    ${random int} =    Evaluate    random.randint(0, 5)    modules=random
    Should Be True    ${rc} < 10    Return code greater than 10
    Run Keyword If    '${status}' == 'PASS'    Log    Passed
    Run Keyword If    'FAIL' in '''${output}'''    Log    Output contains FAIL
    Should Be True    $rc < 10    Return code greater than 10
    Run Keyword If    $status == 'PASS'    Log    Passed
    Run Keyword If    'FAIL' in $output    Log    Output contains FAIL
    Should Be True    len($result) > 1 and $result[1] == 'OK'

Test__BuiltIn__02
    ${str1} =    Catenate    Hello    world
    ${str2} =    Catenate    SEPARATOR=---    Hello    world
    ${str3} =    Catenate    SEPARATOR=    Hello    world

Test__BuiltIn__03_01
    ${result} =    Convert To Binary    10    # Result is 1010
    ${result} =    Convert To Binary    F    base=16    prefix=0b    # Result is 0b1111
    ${result} =    Convert To Binary    -2    prefix=B    length=4    # Result is -B0010
    ${bytes} =    Convert To Bytes    hyvä    # hyv\xe4
    ${bytes} =    Convert To Bytes    \xff\x07    # \xff\x07
    ${bytes} =    Convert To Bytes    82 70    int    # RF
    ${bytes} =    Convert To Bytes    0b10 0x10    int    # \x02\x10
    ${bytes} =    Convert To Bytes    ff 00 07    hex    # \xff\x00\x07
    ${bytes} =    Convert To Bytes    5246212121    hex    # RF!!!
    ${bytes} =    Convert To Bytes    0000 1000    bin    # \x08
    ${input} =    Create List    1    2    12
    ${bytes} =    Convert To Bytes    ${input}    int    # \x01\x02\x0c
    ${bytes} =    Convert To Bytes    ${input}    hex    # \x01\x02\x12

Test__BuiltIn__03_02
    ${result} =    Convert To Hex    255    # Result is FF
    ${result} =    Convert To Hex    -10    prefix=0x    length=2    # Result is -0x0A
    ${result} =    Convert To Hex    255    prefix=X    lowercase=yes    # Result is Xff

Test__BuiltIn__03_03
    ${result} =    Convert To Integer    100    # Result is 100
    ${result} =    Convert To Integer    FF AA    16    # Result is 65450
    ${result} =    Convert To Integer    100    8    # Result is 64
    ${result} =    Convert To Integer    -100    2    # Result is -4
    ${result} =    Convert To Integer    0b100    # Result is 4
    ${result} =    Convert To Integer    -0x100    # Result is -256

Test__BuiltIn__03_04
    &{dict} =    Create Dictionary    key=value    foo=bar    # key=value syntax
    Should Be True    ${dict} == {'key': 'value', 'foo': 'bar'}
    &{dict2} =    Create Dictionary    key    value    foo    bar    # separate key and value
    Should Be Equal    ${dict}    ${dict2}
    &{dict} =    Create Dictionary    ${1}=${2}    &{dict}    foo=new    # using variables
    Should Be True    ${dict} == {1: 2, 'key': 'value', 'foo': 'new'}
    Should Be Equal    ${dict.key}    value    # dot-access

Test__BuiltIn__04
    Should Be Equal    ${x}    ${y}    Custom error    values=True    # Strings are generally true.
    Should Be Equal    ${x}    ${y}    Custom error    values=yes    # Same as the above.
    Should Be Equal    ${x}    ${y}    Custom error    values=${TRUE}    # Python True is true.
    Should Be Equal    ${x}    ${y}    Custom error    values=${42}    # Numbers other than 0 are true.

Test__BuiltIn__05
    ${status} =    Evaluate    0 < ${3.14} < 10    # Would also work with string '3.14'
    ${random} =    Evaluate    random.randint(0, sys.maxint)    modules=random, sys
    ${ns} =    Create Dictionary    x=${4}    y=${2}
    ${result} =    Evaluate    x*10 + y    namespace=${ns}

Test__BuiltIn__06
    ${length} =    Get Length    Hello, world!
    Should Be Equal As Integers    ${length}    13
    @{list} =    Create List    Hello,    world!
    ${length} =    Get Length    ${list}
    Should Be Equal As Integers    ${length}    2

Test__BuiltIn__07
    ${time} =    Get Time
    ${secs} =    Get Time    epoch
    ${year} =    Get Time    return year
    ${yyyy}    ${mm}    ${dd} =    Get Time    year,month,day
    @{time} =    Get Time    year month day hour min sec
    ${y}    ${s} =    Get Time    seconds and year
    ${time} =    Get Time    1177654467    # Time given as epoch seconds
    ${secs} =    Get Time    sec    2007-04-27 09:14:27    # Time given as a timestamp
    ${year} =    Get Time    year    NOW    # The local time of execution
    @{time} =    Get Time    hour min sec    NOW + 1h 2min 3s    # 1h 2min 3s added to the local time
    @{utc} =    Get Time    hour min sec    UTC    # The UTC time of execution
    ${hour} =    Get Time    hour    UTC - 1 hour    # 1h subtracted from the UTC time

Test__BuiltIn__08
    ${x} =    Get Variable Value    ${a}    default
    ${y} =    Get Variable Value    ${a}    ${x}
    ${z} =    Get Variable Value    ${z}
    ${example_variable} =    Set Variable    example value
    ${variables} =    Get Variables
    Dictionary Should Contain Key    ${variables}    \${example_variable}
    Dictionary Should Contain Key    ${variables}    \${ExampleVariable}
    Set To Dictionary    ${variables}    \${name}    value
    Variable Should Not Exist    \${name}
    ${no decoration} =    Get Variables    no_decoration=Yes
    Dictionary Should Contain Key    ${no decoration}    example_variable

Test__BuiltIn__09
    @{LIST} =    Create List    foo    baz
    ${index} =    Find Index    baz    @{LIST}
    Should Be Equal    ${index}    ${1}
    ${index} =    Find Index V2    nonexisting    @{LIST}
    Should Be Equal    ${index}    ${-1}

Test__BuiltIn__10
    ${hi} =    Set Variable    Hello, world!
    ${hi2} =    Set Variable    I said: ${hi}
    ${var1}    ${var2} =    Set Variable    Hello    world
    @{list} =    Set Variable    hello    world
    ${item1}    ${item2} =    Set Variable    hello    world
    ${var1} =    Set Variable If    ${rc} == 0    zero    nonzero
    ${var2} =    Set Variable If    ${rc} > 0    value1    value2
    ${var3} =    Set Variable If    ${rc} > 0    whatever

Test__BuiltIn__11
    ${output} =    Set Variable    1234567
    Should Match Regexp    ${output}    \\d{6}    # Output contains six numbers
    Should Match Regexp    343242    ^\\d{6}$    # Six numbers and nothing more
    Should Not Match Regexp    ${output}    ^\\d{6}$
    ${ret} =    Should Match Regexp    Foo:42    (?i)foo:\\d+
    ${match}    ${group1}    ${group2} =    Should Match Regexp    Bar: 43    (Foo|Bar): (\\d+)

Test__BuiltIn__12

*** Keywords ***
Find Index
    [Arguments]    ${element}    @{items}
    ${index} =    Set Variable    ${0}
    : FOR    ${item}    IN    @{items}
    \    Run Keyword If    '${item}' == '${element}'    Return From Keyword    ${index}
    \    ${index} =    Set Variable    ${index + 1}
    Return From Keyword    ${-1}    # Also [Return] would work here.

Find Index V2
    [Arguments]    ${element}    @{items}
    ${index} =    Set Variable    ${0}
    : FOR    ${item}    IN    @{items}
    \    Return From Keyword If    '${item}' == '${element}'    ${index}
    \    ${index} =    Set Variable    ${index + 1}
    Return From Keyword    ${-1}    # Also [Return] would work here.
