#ls *.py | sed 's/$/ --test/' | xargs -n 1 -P 3 python
ls *.py | grep -v '^_' | xargs -I % sh -c 'python % --test'
