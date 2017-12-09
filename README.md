# auto-diff-edu
Simple automatic differentiation via operator overloading for educational purposes

Test math: <img src="https://rawgit.com/parrt/auto-diff-edu/master//tex/6177db6fc70d94fdb9dbe1907695fce6.svg?invert_in_darkmode" align=middle width=15.947580000000002pt height=26.76201000000001pt/>.

<p align="center"><img src="https://rawgit.com/parrt/auto-diff-edu/master//tex/45bcb54039e646e45cec0be94b284481.svg?invert_in_darkmode" align=middle width=21.049214999999997pt height=36.27789pt/></p>

or <img src="https://rawgit.com/parrt/auto-diff-edu/master//tex/a1b874849f8b8aa121b207dbe8bdf3e7.svg?invert_in_darkmode" align=middle width=20.404395000000005pt height=22.831379999999992pt/> or <img src="https://rawgit.com/parrt/auto-diff-edu/master//tex/31fcef5ad89935bf7afdd77634d19492.svg?invert_in_darkmode" align=middle width=18.08037pt height=30.648420000000016pt/>.

partial deriv op: <img src="https://rawgit.com/parrt/auto-diff-edu/master//tex/d7a7a7e01930b7235d124f3b639ee0fc.svg?invert_in_darkmode" align=middle width=9.395100000000005pt height=14.155350000000013pt/> or <img src="https://rawgit.com/parrt/auto-diff-edu/master//tex/9fc20fb1d3825674c6a279cb0d5ca636.svg?invert_in_darkmode" align=middle width=14.045955000000003pt height=14.155350000000013pt/>.

## Notes

Build README.md from README.tex.md via:

```bash
python -m readme2tex --username parrt --project auto-diff-edu \
  --rerender --svgdir images --usepackage physics \
  --output README.md README.tex.md
```