# auto-diff-edu
Simple automatic differentiation via operator overloading for educational purposes

Test math: $x^2$.

$$
\frac{\partial f}{\partial t_i}
$$

or $\pdv{f}{t_i}$ or $\frac{\partial Q}{\partial t}$.

partial deriv op: $\pderivative{x}$.

## Notes

Build README.md from README.tex.md via:

```bash
python -m readme2tex --username parrt --project auto-diff-edu \
  --rerender --svgdir images --usepackage physics \
  --output README.md README.tex.md
```