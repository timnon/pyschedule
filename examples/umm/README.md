Run athletics-event-scheduler:
$ python umm2019.py saturday --horizon=50 --time-limit=30m -v
$ python umm2019.py saturday --horizon=49 --time-limit=30m --fast -v
$ python umm2019.py saturday --horizon=50 --time-limit=30m --with-ortools -v
$ python umm2019.py sunday --horizon=45 --time-limit=30m -v
$ python umm2019.py sunday --horizon=50 --time-limit=30m --fast -v

Run tests:
$ python -m nose test/test_athletics_event.py

Stuff to read:
- https://github.com/timnon/pyschedule
- https://developers.google.com/optimization/cp
- https://developers.google.com/optimization/reference/python/sat/python/cp_model
- https://google.github.io/or-tools/python/ortools/sat/python/cp_model.html
- https://google.github.io/or-tools/dotnet/namespaceGoogle_1_1OrTools_1_1Sat.html
- https://acrogenesis.com/or-tools/documentation/user_manual/manual/first_steps/monitors.html
- https://www.xiang.dev/cp-sat/#
- https://de.slideshare.net/PhilippeLaborie/introduction-to-cp-optimizer-for-scheduling
- http://www.hakank.org/google_or_tools/