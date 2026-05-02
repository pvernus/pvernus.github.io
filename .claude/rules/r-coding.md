# R Coding Standards

Apply these rules whenever writing or reviewing R scripts in `scripts/`.

---

## Pipe

- **Always use native pipe `|>`** — never magrittr `%>%`
- R 4.3+ is assumed throughout

```r
# Good
data |> filter(year >= 2010) |> summarise(mean(aid), .by = recipient)

# Bad
data %>% filter(year >= 2010) %>% summarise(mean(aid))
```

---

## Joins (dplyr 1.1+)

- **Use `join_by()` instead of `by = c("a" = "b")`**
- Use `multiple` and `unmatched` arguments for quality control on merges

```r
# Good
panel |> left_join(covariates, by = join_by(country == iso3, year))
panel |> inner_join(disasters, by = join_by(country, year), multiple = "error")

# Bad
panel |> left_join(covariates, by = c("country" = "iso3", "year"))
```

---

## Grouping (dplyr 1.1+)

- **Use `.by` for per-operation grouping** — avoids `group_by() |> ungroup()` boilerplate

```r
# Good
data |> summarise(total = sum(aid), .by = c(donor, recipient))

# Bad
data |> group_by(donor, recipient) |> summarise(total = sum(aid)) |> ungroup()
```

---

## purrr (1.0+)

- **Use `map() |> list_rbind()`** instead of superseded `map_dfr()`
- **Use `walk()` for side effects** (saving files, plotting)
- **Use `map_dbl()`, `map_chr()` etc.** instead of `sapply()` — type-stable

```r
# Good
results <- specs |> map(\(s) run_model(s)) |> list_rbind()

# Bad
results <- map_dfr(specs, run_model)   # superseded
results <- sapply(specs, run_model)    # type-unstable
```

---

## Functional form for aid outcomes

- **Never log-transform aid outcomes** — PPML handles zeros structurally
- Use `feglm(..., family = "ppml")` or `fepois()` from `fixest`
- Report marginal effects as percentage changes (semi-elasticities from PPML)

---

## Object persistence

- **`saveRDS()` every computed object** that takes >5 seconds to produce
- Load with `readRDS()` at the top of downstream scripts
- Path convention: `output/paper/img/[object_name].RDS`

---

## Performance

- **Profile before optimizing** — use `profvis::profvis()` to find real bottlenecks
- **Benchmark alternatives** with `bench::mark()` before rewriting
- For datasets >1GB consider `data.table` over `dplyr`
- Pre-allocate result containers; never grow objects in a loop

```r
# Good — pre-allocate
results <- vector("list", length(specs))
for (i in seq_along(specs)) results[[i]] <- run_model(specs[[i]])

# Bad — grows in loop
results <- c()
for (s in specs) results <- c(results, run_model(s))
```

---

## Style

- **`snake_case`** for all variable and function names
- **Function names = verbs**, variable names = nouns
- No dots in names except for S3 methods (`print.my_class`)
- `set.seed()` once at the top of any script with stochastic elements
- No hardcoded absolute paths — all paths relative to project root

---

## Anti-patterns to flag in code review

| Pattern | Replacement |
|---------|-------------|
| `%>%` | `\|>` |
| `by = c("a" = "b")` | `join_by(a == b)` |
| `group_by() \|> … \|> ungroup()` | `.by` argument |
| `map_dfr()` / `map_dfc()` | `map() \|> list_rbind()` / `list_cbind()` |
| `sapply()` | `map_dbl()`, `map_chr()`, etc. |
| `log(outcome)` for aid | PPML levels |
| Hardcoded path `C:/Users/…` | Relative path |
