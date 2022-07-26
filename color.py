[38;5;28;01mfrom[39;00m [38;5;21;01mpygments[39;00m[38;5;21;01m.[39;00m[38;5;21;01mlexers[39;00m [38;5;28;01mimport[39;00m PythonLexer
[38;5;28;01mfrom[39;00m [38;5;21;01mpygments[39;00m[38;5;21;01m.[39;00m[38;5;21;01mformatters[39;00m [38;5;28;01mimport[39;00m TerminalFormatter
[38;5;28;01mfrom[39;00m [38;5;21;01mpygments[39;00m [38;5;28;01mimport[39;00m highlight

source_code [38;5;241m=[39m [38;5;124m'''[39m
[38;5;124mimport requests[39m

[38;5;124mdef fun():[39m
[38;5;124m  print([39m[38;5;124m'[39m[38;5;124mHello[39m[38;5;124m'[39m[38;5;124m)[39m
[38;5;124m'''[39m

[38;5;28mprint[39m(highlight(source_code, PythonLexer(), TerminalFormatter()))
