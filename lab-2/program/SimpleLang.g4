grammar SimpleLang;

prog: stat+ EOF ;

stat: expr NEWLINE ;

expr: expr op=('*'|'/'|'%') expr   # MulDivMod
    | expr op=('+'|'-') expr       # AddSub
    | expr op='==' expr            # Equality
    | INT                          # Int
    | FLOAT                        # Float
    | STRING                       # String
    | BOOL                         # Bool
    | '(' expr ')'                 # Parens
    ;

INT: [0-9]+ ;
FLOAT: [0-9]+'.'[0-9]* ;
STRING: '"' .*? '"' ;
BOOL: 'true' | 'false' ;
NEWLINE: '\r'? '\n' ;
WS: [ \t]+ -> skip ;
