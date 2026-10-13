// Build the combined manuscript and Supplementary Information (.docx).
// Run from the repository root:  node combined/build_manuscript.js
// Every number in new sections and tables is read from combined/combined_numbers.json.
// Reference-analysis prose (Sections 2.1-2.6, 3.1-3.8) carries the v5 values, which are
// checked against data/manuscript_numbers.json by combined/verify_combined_manuscript.py.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun, AlignmentType,
  HeadingLevel, WidthType, BorderStyle, Footer, PageNumber, ShadingType, VerticalAlign,
  Math: OMath, MathRun, MathFraction, MathSubScript, MathSuperScript, MathSubSuperScript,
  PageBreak, TableLayoutType,
} = require("docx");

const ROOT = path.resolve(__dirname, "..");
const N = JSON.parse(fs.readFileSync(path.join(ROOT, "combined/combined_numbers.json"), "utf8"));
const X = JSON.parse(fs.readFileSync(path.join(ROOT, "combined/component_comparison.json"), "utf8"));
const V5 = N.v5;
const FIG = path.join(ROOT, "combined/figures");
const OUT = path.join(ROOT, "combined/manuscript");
fs.mkdirSync(OUT, { recursive: true });

// ---------------- number formatting ----------------
const f = (x, d = 3) => (x < 0 && Math.abs(x) >= 0.5 * Math.pow(10, -d) ? "−" : "") + Math.abs(x).toFixed(d);
const ci = (t, d = 3) => `${f(t[0], d)} [${f(t[1], d)}, ${f(t[2], d)}]`;
const ciB = (t, d = 3) => `${f(t[0], d)}\n[${f(t[1], d)}, ${f(t[2], d)}]`; // two-line cell form
const pc = (x, d = 1) => (x * 100).toFixed(d) + "%";
const pcn = (x, d = 1) => (x * 100).toFixed(d);
const n = (x) => Number(x).toLocaleString("en-US");
const M = N.models;
const SH = N.short;
const C = N.corpus;
const common = N.all_model_common;

// ---------------- supplementary-table numbering ----------------
const STN = {};
let stCount = 0;
const st = (k) => STN[k] || (STN[k] = ++stCount);
const resolveST = (t) => t.replace(/§ST:(\w+)§/g, (_, k) => String(st(k)));

// ---------------- text helpers ----------------
const FONT = "Times New Roman";
function runs(text, base = {}) {
  text = resolveST(text);
  const out = [];
  const re = /(_\{[^}]*\}|\^\{[^}]*\}|\*[^*\s][^*]*\*)/g;
  // sub/superscript contents may themselves contain *italic* segments
  const inner = (t, extra) => {
    const parts = [];
    const ri = /\*([^*]+)\*/g;
    let l = 0, mm;
    while ((mm = ri.exec(t)) !== null) {
      if (mm.index > l) parts.push(new TextRun({ text: t.slice(l, mm.index), ...base, ...extra }));
      parts.push(new TextRun({ text: mm[1], italics: true, ...base, ...extra }));
      l = mm.index + mm[0].length;
    }
    if (l < t.length) parts.push(new TextRun({ text: t.slice(l), ...base, ...extra }));
    return parts;
  };
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), ...base }));
    const tok = m[0];
    if (tok.startsWith("_{")) out.push(...inner(tok.slice(2, -1), { subScript: true }));
    else if (tok.startsWith("^{")) out.push(...inner(tok.slice(2, -1), { superScript: true }));
    else out.push(new TextRun({ text: tok.slice(1, -1), italics: true, ...base }));
    last = m.index + tok.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), ...base }));
  return out;
}
const P = (text, opt = {}) => new Paragraph({ children: runs(text, opt.run || {}), spacing: { after: 120, line: 300 }, alignment: AlignmentType.JUSTIFIED, ...opt.para });
const H1 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(text)] });
const H2 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(text)] });
const CAP = (label, text) => new Paragraph({ keepLines: true, spacing: { before: 60, after: 200, line: 260 }, alignment: AlignmentType.JUSTIFIED,
  children: [new TextRun({ text: label + " ", bold: true, size: 20 }), ...runs(text, { size: 20 })] });
const TCAP = (label, text) => new Paragraph({ keepLines: true, spacing: { before: 200, after: 80, line: 260 }, keepNext: true, alignment: AlignmentType.JUSTIFIED,
  children: [new TextRun({ text: label + " ", bold: true, size: 20 }), ...runs(text, { size: 20 })] });
const NOTE = (text) => new Paragraph({ spacing: { before: 40, after: 200, line: 240 }, alignment: AlignmentType.JUSTIFIED, children: runs(text, { size: 18 }) });

// ---------------- equations ----------------
// r(): italic math run (variables); u(): upright run (units, labels, function names).
// Upright runs carry a sentinel that is converted to <m:sty m:val="p"/> after packing.
const UP = "\u2063";
const r = (t) => new MathRun(t);
const u = (t) => new MathRun(UP + t);
const sub = (b, s, italicSub = false) => new MathSubScript({ children: [typeof b === "string" ? r(b) : b], subScript: [italicSub ? r(s) : u(s)] });
const subI = (b, s) => sub(b, s, true);
const sup = (bChildren, s) => new MathSuperScript({ children: bChildren, superScript: Array.isArray(s) ? s : [r(s)] });
const frac = (a, b) => new MathFraction({ numerator: a, denominator: b });
function EQ(children, num) {
  return new Paragraph({ alignment: AlignmentType.LEFT, spacing: { before: 80, after: 120 },
    tabStops: [{ type: "center", position: 4513 }, { type: "right", position: 9026 }],
    children: [new TextRun("\t"), new OMath({ children }), new TextRun(`\t(${num})`)] });
}
// ---------------- tables ----------------
const CW = 9026; // content width in twips (A4, 1-inch margins)
const thin = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
function cell(text, w, { bold = false, head = false, align = AlignmentType.LEFT, last = false } = {}) {
  return new TableCell({
    width: { size: w, type: WidthType.DXA },
    margins: { top: 40, bottom: 40, left: 70, right: 70 },
    verticalAlign: VerticalAlign.CENTER,
    borders: { top: head ? thin : none, bottom: head || last ? thin : none, left: none, right: none },
    children: String(text).split("\n").map((t) => new Paragraph({ alignment: align, spacing: { after: 0, line: 240 }, children: runs(t, { size: 18, bold: bold || head }) })),
  });
}
function TABLE(headers, rows, widths) {
  const total = widths.reduce((a, b) => a + b, 0);
  const w = widths.map((x) => Math.round((x / total) * CW));
  w[w.length - 1] += CW - w.reduce((a, b) => a + b, 0);
  const al = (i) => (i === 0 ? AlignmentType.LEFT : AlignmentType.CENTER);
  return new Table({
    width: { size: CW, type: WidthType.DXA }, columnWidths: w, layout: TableLayoutType.FIXED,
    rows: [
      new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, w[i], { head: true, align: al(i) })) }),
      ...rows.map((row, ri) => new TableRow({ cantSplit: true, children: row.map((c, i) => cell(c, w[i], { align: al(i), last: ri === rows.length - 1 })) })),
    ],
  });
}

// ---------------- figures ----------------
function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20), data: b };
}
function FIGURE(name, widthIn = 6.27) {
  const s = pngSize(path.join(FIG, name + ".png"));
  const wpx = Math.round(widthIn * 96);
  return new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 160, after: 60 },
    children: [new ImageRun({ type: "png", data: s.data, transformation: { width: wpx, height: Math.round((wpx * s.h) / s.w) },
      altText: { title: name, description: name, name } })] });
}

// ---------------- document styles ----------------
const styles = {
  default: { document: { run: { font: FONT, size: 22 } } },
  paragraphStyles: [
    { id: "Title", name: "Title", basedOn: "Normal", run: { font: FONT, size: 32, bold: true }, paragraph: { spacing: { after: 240 }, alignment: AlignmentType.CENTER } },
    { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 26, bold: true }, paragraph: { spacing: { before: 300, after: 140 }, outlineLevel: 0, keepNext: true } },
    { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 23, bold: true, italics: true }, paragraph: { spacing: { before: 220, after: 100 }, outlineLevel: 1, keepNext: true } },
  ],
};
const page = { size: { width: 11906, height: 16838 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } };
const footer = () => ({ default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], size: 18 })] })] }) });

// =====================================================================================
// Numbers used in new sections
// =====================================================================================
const nu = N.narrow_upturn_native;
const sc = N.stress_common;
const up = sc.narrow_upturn;
const ctl = N.control_narrow;
const same = N.same_model_test;
const sel = N.selection;
const tx = {};
N.transfer.forEach((t) => (tx[t.inference + "|" + t.truth] = t));
const cb = (m) => C[m].all_model_common.CB;
const ca = (m) => C[m].all_model_common.CA;
const VAR = M.filter((m) => m !== "baseline");
const sameCov = VAR.map((m) => same[m].lattice_coverage);
const ratio = N.strata_ratio_top_bottom;
const ratios = M.map((m) => ratio[m]);
const famCells = M.flatMap((m) => Object.entries(N.families[m]).map(([k, v]) => ({ m, k, v })));
const famIncl0 = famCells.filter((x) => x.v.CB[2] >= 0);
const famNeg = famCells.filter((x) => x.v.CB[0] < 0);
const adm = M.map((m) => sel[m].admitted);
const nat = M.map((m) => C[m].native.n);
const widthRatio = up.models.mobility_spline.lattice_width / up.models.baseline.lattice_width;
const thrSpline = N.threshold_range_CB.spline;
const extraMax = 0.05 * Math.pow(750 / 300, 3);
if (famNeg.length !== famCells.length) throw new Error("a family median is non-negative; revise text");

// =====================================================================================
// MAIN TEXT
// =====================================================================================
const T = [];
T.push(new Paragraph({ style: "Title", children: [new TextRun("Bipolar heat and model-dependent estimates of lattice thermal conductivity across a thermoelectric corpus")] }));
T.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 360 }, children: [new TextRun({ text: "[Author names and affiliations to be completed by the authors]", italics: true })] }));

T.push(H1("Abstract"));
T.push(P(`Lattice thermal conductivity inferred by unipolar subtraction can contain bipolar heat. We analyse ${n(V5.n)} literature-derived transport curves with a two-band neural posterior estimator and five extensions that relax shared carrier parameters, lattice monotonicity or thermal-channel assumptions. In the reference model, replacing the Lorenz estimator changes the median 400–750 K log-slope by ${f(V5.shifts.BA[0])}, whereas the model lattice estimate shifts it by ${f(V5.shifts.CB[0])} relative to the unipolar remainder. The shift varies with material family, inferred bipolar share and measured Seebeck rollover. On ${n(common.n)} curves selected by all six models, the median shift remains negative but ranges from ${f(cb("baseline")[0])} to ${f(cb("mobility_spline")[0])}. On 509 common synthetic lattice-upturn cases, flexible independent-band inference raises nominal 95% lattice coverage from ${pc(up.models.baseline.lattice_coverage)} to ${pc(up.models.mobility_spline.lattice_coverage)} while widening intervals about ${Math.round(widthRatio)}-fold; absolute slope error does not improve on the 87 common slope-eligible cases. Same-model undercoverage and cross-model attribution failures persist. The direction of the selected-population shift is stable across the tested hypotheses, while its magnitude and physical attribution remain model-dependent. These results do not establish errors in source publications.`));

// ---------------- 1. Introduction ----------------
T.push(H1("1. Introduction"));
T.push(P("The figure of merit *zT* = *S*^{2}σ*T*/κ combines measured electrical conductivity, Seebeck coefficient and total thermal conductivity. Separating lattice heat requires additional assumptions. A widely used approximation is κ_{L} = κ − *L*σ*T*, with *L* inferred from *S*. The single-parabolic-band estimator of Kim et al. [1] is *L* = [1.5 + exp(−|*S*|/116)] × 10^{−8} W Ω K^{−2}, where *S* is expressed in µV K^{−1}. Its applicability depends on the assumed carrier and scattering regime."));
T.push(P("With two carrier types, the unipolar electronic contribution is κ_{e} = (*L*_{p}σ_{p} + *L*_{n}σ_{n})*T*, and an additional term is κ_{bip} = [σ_{p}σ_{n}/(σ_{p} + σ_{n})](*S*_{p} − *S*_{n})^{2}*T*, using signed band Seebeck coefficients. In the absence of an additional thermal channel, subtracting only κ_{e} leaves κ_{L} + κ_{bip}. An effective Lorenz number defined to include bipolar heat would instead absorb this term. Specifying the Lorenz convention is therefore essential."));
T.push(P("Single-material studies already treat bipolar transport explicitly [10,11]. Other mechanisms also affect subtraction: electrically resistive grain boundaries can produce an overestimate [8], and departures from simple scattering can alter the Lorenz number [9]. We quantify the results of applying one conventional subtraction uniformly to a frozen literature-derived corpus and compare them with a stated joint model. We do not establish which subtraction each source author used."));
T.push(P("Amortised simulation-based inference [2,3] makes repeated approximate inference practical after training on simulator output. Its uncertainty must be checked against held-out simulations [4]. Here we distinguish tests of raw Gaussian ellipsoids from coverage of the constrained draws and derived heat channels used in the analysis."));
T.push(P("The inferred thermal decomposition depends on the assumptions of the forward model. The reference model imposes two structural restrictions: the two bands share their mobility prefactor, mobility temperature exponent and scattering exponent, and the lattice term can only decrease with temperature. Genuine lattice upturns have been reported, for example in cubic GeTe [7], and synthetic stress tests show that both restrictions can bias channel estimates. We therefore train five further estimators that relax them, separately and together, and use independent same-model simulations, shared stress tests and selection-controlled corpus comparisons to ask which conclusions survive the change of model."));
T.push(P("The analysis provides a reproducible transport model, a corpus comparison of four thermal estimates, a six-model robustness analysis that separates the direction of the bipolar-associated shift from its magnitude, and conditional posterior summaries of an effective scattering exponent. Conclusions remain conditional on the priors, observation model, Gaussian approximation and the families of carrier and lattice behaviour that were tested."));

// ---------------- 2. Methods ----------------
T.push(H1("2. Methods"));
T.push(H2("2.1 Corpus"));
T.push(P(`The analysis set contains ${n(V5.n)} literature-derived transport records from ${n(V5.papers)} source papers in Starrydata [5]. Each record contains σ(*T*), *S*(*T*) and total κ(*T*), together with a sample identifier, source DOI and family label. We verify the released sample list against the official ThermoelectricMaterials export with database snapshot 9 October 2026, joining on source paper and sample rather than integer sample identifier alone. The dated release, SHA-256 checksums and selection manifest are archived.`));
T.push(P("The released sample list defines a literature cohort rather than an exhaustive census of Starrydata. Eligibility requires a common temperature span of at least 200 K, a 300 K lower floor, an upper endpoint at or below 1250 K and a lower endpoint at or below 500 K. Conductivity is used when available; otherwise resistivity is inverted after interpolation. The underlying historical selection included an unavailable plausibility-screen implementation, so the list and source-verification criteria, rather than a reconstructed database-wide selection rule, define reproducibility. Records without a source-matched, unambiguous usable curve for every required channel, or failing transport reproduction, are excluded."));
T.push(P("The total thermal-conductivity field is distinguished from source-reported lattice conductivity. Canonical property labels, SI units and temperature coverage are checked before comparison on the 16-point grid. Identical repeated points may be collapsed; conflicting values at one temperature require source review and are not interpolated automatically. Maximum discrepancies must not exceed 1% for σ and κ, with an absolute allowance of 0.001 S m^{−1} for near-zero σ, and 1 µV K^{−1} for *S*. Endpoint rounding of up to 0.0001 K is allowed. Passing these checks establishes source consistency, not physical correctness of a measurement."));
T.push(P("The 50 features are log_{10} σ, *S* in µV K^{−1} and ln κ at 16 temperatures, followed by *T*_{hi}/1000 and *T*_{lo}/1000, in that order. Frozen numerical values preserve the downstream analysis against later database changes."));

T.push(H2("2.2 Forward model"));
T.push(P("The simulator is a two-band single-parabolic-band model. Carrier densities are solved from charge neutrality, *n*_{maj}(η_{maj},*T*) − *n*_{min}(η_{min},*T*) = *N*_{net}, where *N*_{net} > 0 is the magnitude of the net dopant density and η_{min} = −η_{maj} − *E*_{g}/(*k*_{B}*T*), by bisection at each temperature, so thermally activated behaviour in which σ rises with temperature emerges from the physics rather than being imposed. The solver expands its bracket and checks the neutrality residual. For *N*_{net} = 10^{21} cm^{−3} and majority mass 10^{−1.3} *m*_{e} at 300 K, η ≈ 281.43 is resolved rather than silently limited to 40. Forward inputs are promoted to double precision. The sign head assigns holes or electrons to the majority band and reverses the signed Seebeck coefficients accordingly. In the physical hole/electron convention, *p* − *n* equals +*N*_{net} for p-type and −*N*_{net} for n-type material."));
T.push(P("The corrected implementation uses unnormalised Fermi–Dirac integrals. Within −20 ≤ η ≤ 50, a quadrature table has spacing 0.01 in order and 0.025 in η, with cubic interpolation in order and linear interpolation in η on log integrals. Quadrature uses ε = *u*^{4} and 512 Gauss–Legendre nodes. Explicit Boltzmann and Sommerfeld expansions supply the tails; values are not clamped. Independent numerical integration on 63 selected order–η combinations gave a maximum relative integral discrepancy of 1.56 × 10^{−5}. This finite check is not a uniform error bound over every parameter combination."));
T.push(P("Relaxation time is τ ∝ ε^{*r*}. The mobility of band *j* is"));
T.push(EQ([subI("μ", "j"), r("("), r("T"), u(","), subI("η", "j"), u(")="), new MathSubScript({ children: [r("μ")], subScript: [r("j"), u(",300")] }),
  sup([u("("), frac([r("T")], [u("300 K")]), u(")")], [subI("p", "j")]),
  frac([new MathSubScript({ children: [r("F")], subScript: [subI("r", "j"), u("+1/2")] }), u("("), subI("η", "j"), u(")")], [new MathSubScript({ children: [r("F")], subScript: [u("1/2")] }), u("("), subI("η", "j"), u(")")]),
  frac([u("Γ(3/2)")], [u("Γ("), subI("r", "j"), u("+3/2)")])], 1));
T.push(P("where the last factor makes μ_{*j*,300} the non-degenerate 300 K mobility irrespective of *r*, so that its prior can be set from literature values. Total thermal conductivity is", { para: { alignment: AlignmentType.LEFT } }));
T.push(EQ([r("κ"), u("="), sub("κ", "e"), u("+"), sub("κ", "bip"), u("+"), sub("κ", "L"), u(",\u2003"), sub("κ", "L"), u("="), sub("κ", "min"), u("+"), r("A"), sup([u("("), frac([u("300 K")], [r("T")]), u(")")], "w")], 2));
T.push(P("with *w* ≥ 0 in the reference model. The bipolar term is", { para: { alignment: AlignmentType.LEFT } }));
T.push(EQ([sub("κ", "bip"), u("="), frac([sub("σ", "p"), sub("σ", "n")], [sub("σ", "p"), u("+"), sub("σ", "n")]), sup([u("("), sub("S", "p"), u("−"), sub("S", "n"), u(")")], [u("2")]), r("T")], 3));
T.push(P("The model reproduces both analytic Lorenz limits to better than 5 × 10^{−3} at *r* = −1.0, 0.0 and +2.0, and κ_{bip} peaks at equal channel conductivity when the total is held fixed."));
T.push(P("The reference simulator shares *r*, the mobility temperature exponent *p*_{μ} and the non-degenerate 300 K mobility between bands; masses and Fermi levels may differ. Section 2.7 defines the extended models that relax these equalities and the monotone lattice form."));

T.push(H2("2.3 Prior"));
T.push(P("Ten continuous parameters and a binary majority-carrier sign are inferred in the reference model. Uniform draws within Table 1 are independent except for the doping-dependent mobility interval; each sign has probability one half. Measurement endpoints are sampled within their bounds and rejected until *T*_{hi} − *T*_{lo} ≥ 200 K. The prior also requires maximum *zT* ≤ 3.5 on the 16-point window grid. Bounds are inherited from the supplied study, rather than independently selected on a new real-data corpus."));
T.push(P("For each simulated observation, 8–20 uniformly spaced temperature points are used. Independent factors exp(ε), with ε ∼ Normal(0, 0.02^{2}), perturb each property before interpolation onto 16 feature temperatures. This induces interpolation correlations but lacks shared calibration errors, additive Seebeck error and property-specific uncertainty. It is not a complete experimental-error model."));
T.push(TCAP("Table 1.", "Reference-model prior bounds. Masses are relative to the electron mass; mobility is in cm^{2} V^{−1} s^{−1}. Conditional mobility bounds and the *zT* restriction are enforced at inference and simulation. The lattice floor is included in κ_{L}, total κ and *zT*. Extended-model parameters are listed in Section 2.7."));
T.push(TABLE(["Parameter", "Lower", "Upper", "Units / note"], [
  ["log_{10} *N*_{net}", "16.0", "21.0", "cm^{−3}"],
  ["log_{10} *m*_{maj}^{*}", "−1.3", "0.7", "*m*_{e}"],
  ["log_{10} *m*_{min}^{*}", "−1.7", "1.0", "*m*_{e}"],
  ["log_{10} μ_{300}", "*c* − 1.8", "*c* + 1.2", "cm^{2} V^{−1} s^{−1}; *c* = 3.1 − 0.5(log_{10} *N* − 17)"],
  ["*p*_{μ}", "−3.5", "2.0", "μ ∝ *T*^{*p*μ}; non-degenerate prefactor, degenerate scaling also depends on *r*"],
  ["log_{10} *E*_{g}", "−1.5", "0.55", "eV (0.03–3.5)"],
  ["log_{10} *A*", "−1.0", "1.2", "W m^{−1} K^{−1}"],
  ["*w*", "0.0", "3.0", "κ_{L} = κ_{min} + *A*(300 K/*T*)^{*w*}"],
  ["*r*", "−1.0", "2.0", "τ ∝ ε^{*r*}"],
  ["κ_{min}", "0.0", "0.70", "W m^{−1} K^{−1}"],
  ["*T*_{lo}", "285", "500", "K; measurement window, sampled"],
  ["*T*_{hi}", "500", "1250", "K; with *T*_{hi} − *T*_{lo} ≥ 200 K"],
], [1.3, 0.8, 0.8, 3.6]));

T.push(H2("2.4 Amortised posterior"));
T.push(P("The network has three hidden layers of 256 SiLU units. It predicts *D* standardised means, *D* log diagonal and *D*(*D* − 1)/2 off-diagonal entries of a lower-triangular precision factor *A*, plus a Bernoulli sign logit; *D* = 10 for the reference model. Precision is *AA*^{T}; Gaussian draws solve *A*^{T}*v* = ε before restoring parameter scale. Continuous and sign heads factorise conditionally on the features. Diagonal log factors are clipped to [−3, 6] before exponentiation; strictly lower-triangular factors are unconstrained. Continuous-head weights and biases are initialised to zero. A single Gaussian cannot generally represent multimodal or strongly non-Gaussian posteriors. The per-example training objective is"));
T.push(EQ([r("ℓ"), u("="), frac([u("1")], [u("2")]), sup([u("‖"), sup([r("A")], [u("T")]), u("("), r("y"), u("−"), r("μ"), u(")‖")], [u("2")]), u("−"), new MathSubScript({ children: [u("∑")], subScript: [r("i")] }), subI("d", "i"), u("+"), frac([r("D")], [u("2")]), u("ln(2π)+BCE("), r("a"), u(","), r("s"), u(")")], 4));
T.push(P("where *A*_{ii} = exp(*d*_{i}), *y* are the standardised continuous parameters, *s* the carrier sign and *a* its logit. No experimental channel labels enter the loss."));
T.push(P("The corrected reference run uses 600,000 simulations generated with seed 2001. A seed-3 permutation allocates 588,000 for training and 12,000 for validation. Normalisation uses training examples only. The architecture is retained for comparability; architecture experiments using a different simulator do not validate this checkpoint."));
T.push(TCAP("Table 2.", "Reference training configuration and outcome. Validation selects the checkpoint; separate calibration and test simulations are not used for optimisation or checkpoint selection. Extended-model training outcomes are in Supplementary Table §ST:training§."));
T.push(TABLE(["Quantity", "Value"], [
  ["Training / validation", "588,000 / 12,000"],
  ["Calibration / independent test", "6,000 / 6,000"],
  ["Hidden layers", "3 × 256 SiLU"],
  ["Continuous head", "Full Gaussian precision"],
  ["Optimiser / batch", "AdamW / 1024"],
  ["Selected epoch / completed (one-based)", `${N.reference_training.selected_epoch_one_based} / ${N.reference_training.epochs_completed}`],
  ["Best validation NLL", "−7.1647"],
  ["Stopping condition", "epoch_cap"],
], [2, 2]));
T.push(P("Training uses AdamW, initial learning rate 0.0015, weight decay 10^{−5}, batches of 1024 and gradient clipping at norm 5. ReduceLROnPlateau has factor 0.5 and patience 6. The cap is 900 epochs; early stopping requires 50 epochs without an improvement of at least 10^{−4}. The run stopped by epoch_cap after 900 epochs, selecting epoch 890 (one-based; stored index 889) with validation negative log likelihood −7.1647 in standardised coordinates. Training seed is 0; device and library versions are archived."));
T.push(P("The full precision factor represents correlations, but physical degeneracies remain, including density–mobility and lattice amplitude–floor trade-offs. The availability of a covariance estimate does not establish accurate uncertainty; independent diagnostics test selected consequences."));

T.push(H2("2.5 Calibration"));
T.push(P("Independent sets of 6,000 simulations each use seeds 2002 and 2003. The first estimates empirical Mahalanobis thresholds for a diagnostic rank map. The second tests these and raw Gaussian thresholds. This map relabels ellipsoid probabilities; it is not used to modify the constrained sampler."));
T.push(P("The reference run uses 588,000 training, 12,000 validation, 6,000 diagnostic calibration and 6,000 independent test simulations: 612,000 base-model examples. Training data can be regenerated from the archived seed and configuration; training configuration and ellipsoid diagnostics are summarised in Table 2 and Table 3."));
T.push(P("We also assess empirical coverage of nominal 95% marginal intervals for all continuous parameters and pointwise intervals for κ_{L}, κ_{bip}, the unipolar Lorenz number and total κ, using the final constrained draws. Rates are conditional on scored independent test curves, with unscored counts reported separately. These finite-sample checks are not full joint simulation-based rank calibration."));
T.push(TCAP("Table 3.", "Independent coverage of raw Gaussian ellipsoids and diagnostic empirically relabelled ellipsoids (reference model). The second row does not describe the constrained draws used for corpus inference; their derived-channel coverage is reported separately."));
T.push(TABLE(["Ellipsoid threshold", "50%", "90%", "95%", "99%"], [
  ["Raw", "57.7%", "89.0%", "93.3%", "96.9%"],
  ["Diagnostic rank map", "50.2%", "90.0%", "95.2%", "99.2%"],
], [2, 1, 1, 1, 1]));
T.push(P("Prior restriction changes the distribution, so ellipsoid coverage cannot certify the constrained sampler. Marginal or pointwise coverage also differs from simultaneous coverage of an entire curve. These tests characterise approximation error rather than declare calibration by construction. On 5,996 scored independent test curves out of 6,000, nominal 95% pointwise coverage was 94.2% for κ_{L}, 93.2% for κ_{bip}, 89.3% for *L*_{uni} and 98.7% for total κ. Parameter coverages ranged from 84.4% to 90.5%."));

T.push(H2("2.6 Applicability domain and statistics"));
T.push(P("For each curve, up to 8,192 Gaussian proposals are considered in batches until 128 draws satisfy the conditional prior and 16-point *zT* restriction. At least 64 are needed for scoring. The sign is sampled from the Bernoulli head. Draws are propagated through the corrected training simulator. A nested-prefix draw-count check on 509 independent test cases with all 256 draws retained gave lattice coverage 94.4% with 128 draws and 95.0% with 256; bipolar coverage changed from 91.8% to 93.2%. The median absolute change in the lattice point estimate was 0.0030 W m^{−1} K^{−1}. This finite subset check does not establish convergence for every real curve."));
T.push(P("The fit screen counts how many of 48 observed values lie inside the pointwise 2.5th–97.5th percentile bands of latent simulated curves. Containment of at least 0.75 admits a curve. Observation noise is not added. This operational screen is not a calibrated significance test, and omission of noise does not make every downstream conclusion conservative."));
T.push(P("Every accepted draw satisfies conditional mobility bounds and maximum *zT* ≤ 3.5 on the stated grid. Computationally unscored curves are distinguished from scored exclusions. Neither category alone identifies a physical cause of disagreement."));
T.push(P("Main intervals use 2,000 percentile bootstrap resamples of source papers, seed 2024. Only papers represented in the finite reported subset are sampled. All curves of a sampled paper are retained, including multiplicity when it is selected more than once. The estimand is a median over curves, not an equal-paper-weighted median."));
T.push(P("These intervals describe variation of posterior summaries across sampled papers, without full within-curve uncertainty. A nested analysis, seed 2025, also selects one matched posterior draw per unique curve in each paper resample. Repeated copies of a curve share that selected draw. Draw-specific non-positive endpoints are omitted from that resample’s logarithmic statistic and their counts are archived; the valid-draw population can therefore differ from the summary-based one."));
T.push(P(`For C − B, the nested 95% interval is [${f(V5.nested_intervals.CB[0])}, ${f(V5.nested_intervals.CB[2])}], with bootstrap median ${f(V5.nested_intervals.CB[1])}; the summary-based estimate is ${ci(V5.shifts.CB)}. A slope of a median curve and a median of draw-specific slopes are distinct nonlinear estimands, not exact reconstructions of one another.`));
T.push(P("Headline slopes use the finite-window log slope"));
T.push(EQ([u("slope="), frac([u("ln["), sub("κ", "X"), u("(750 K)/"), sub("κ", "X"), u("(400 K)]")], [u("ln(750/400)")])], 5));
T.push(P(`for each estimate X. Of ${n(V5.window)} admitted curves spanning 400–750 K, ${n(V5.paired)} have positive finite endpoints for all four estimates (${n(V5.window_papers)} papers). The remaining ${V5.window_nonpositive_excluded} are excluded from logarithmic comparisons rather than floored. Counts for other analyses are stated separately.`));

// ---------------- 2.7 / 2.8 new methods ----------------
T.push(H2("2.7 Extended carrier and thermal models"));
T.push(P(`Five extended models relax the reference restrictions. In the *independent-band* variants, the minority band receives its own temperature exponent *p*_{μ,min}, uniform on [−3.5, 2], and scattering exponent *r*_{min}, uniform on [−1, 2], which enter both its mobility (equation 1) and its transport integrals. Log_{10} of the minority-to-majority non-degenerate 300 K mobility-prefactor ratio is uniform on [−1, 1]; the majority prefactor keeps the doping-dependent prior. The prefactor ratio is not a fixed ratio of actual mobilities at all temperatures. The reference model is recovered when the ratio is one and the exponents match, and this nesting was checked numerically, including on the released mobility-ratio stress cases.`));
T.push(P("The *rising-channel* variants keep the reference lattice form and add a distinct contribution"));
T.push(EQ([r("κ"), u("="), sub("κ", "e"), u("+"), sub("κ", "bip"), u("+"), sub("κ", "L"), u("+"), sub("κ", "extra"), u(",\u2003"), sub("κ", "extra"), u("="), r("B"), sup([u("("), frac([r("T")], [u("300 K")]), u(")")], [u("3")])], 6));
T.push(P(`with *B* uniform on [0, 0.05] W m^{−1} K^{−1}, so κ_{extra} is at most ${f(extraMax, 5)} W m^{−1} K^{−1} at 750 K. The extra term is not identified as phonon or radiative heat; the cubic shape is a chosen hypothesis. Because *B* has a continuous non-negative prior, its posterior positivity is not evidence that a separate mechanism exists. In this family the lattice term itself remains non-increasing.`));
T.push(P("The *flexible-lattice* variants replace equation 2’s lattice term by a positive monotonicity-preserving piecewise cubic Hermite interpolant (PCHIP) [12] in log conductivity versus log temperature,"));
T.push(EQ([new MathSubScript({ children: [u("log")], subScript: [u("10")] }), sub("κ", "L"), u("("), r("T"), u(")="), r("g"), u("(ln "), r("T"), u("),\u2003"), r("g"), u("(ln "), subI("T", "k"), u(")="), subI("g", "k"), u(",\u2003"), r("k"), u("=1,…,6")], 7));
T.push(P("with nodes *T*_{k} = 285, 400, 550, 750, 1000 and 1250 K and node values *g*_{k} independently uniform on [−3, 2] (0.001–100 W m^{−1} K^{−1}). This permits increasing, decreasing and turning lattice curves while guaranteeing positivity. It does not exactly nest the floor-plus-power-law family, and knot placement and the broad independent-node prior are assumptions. The support was widened after inspecting the inherited benchmarks: 44 of 1,000 narrow-gap upturn curves exceeded an initial upper bound of 30 W m^{−1} K^{−1}, and two of 6,000 base test curves fell below an initial lower bound of 0.01 W m^{−1} K^{−1}. The inherited stress sets are therefore development benchmarks rather than untouched tests of model choice; the narrower-prior run is archived separately and excluded from all tables."));
T.push(P(`The five variants are independent bands (*D* = ${N.dimension.mobility}), rising channel (${N.dimension.extra}), flexible lattice (${N.dimension.spline}), independent bands with a rising channel (${N.dimension.mobility_extra}), and independent bands with a flexible lattice (${N.dimension.mobility_spline}); the reference model has ${N.dimension.baseline} continuous parameters. All other prior components, the observation model and the peak-*zT* restriction are unchanged. The variants differ in dimension, prior range and attribution as well as in physical hypothesis, so performance differences cannot be ascribed to one mechanism independently of these choices.`));

T.push(H2("2.8 Extended-model training, testing and comparison populations"));
T.push(P(`Each variant is trained exactly as the reference model (Section 2.4), with the dimension-adjusted precision head, 588,000 training and 12,000 validation simulations, and the same split, optimiser and early-stopping rule. Training seeds are ${VAR.map((m) => N.training[m].seed).join(", ")} in the order above; runs completed ${Math.min(...VAR.map((m) => N.training[m].epochs_completed))}–${Math.max(...VAR.map((m) => N.training[m].epochs_completed))} epochs (Supplementary Table §ST:training§, Supplementary Fig. 1). Only one training seed per variant was evaluated, and reaching the epoch cap is not a convergence certificate. Validation NLL values are not comparable across targets of different dimension. The reference checkpoint is not retrained; its archived inference arrays are the comparator.`));
T.push(P("Each variant is tested on 6,000 new independently seeded simulations from its own prior. Shared stress sets assess selected departures: a 1,000-curve narrow-gap set (gaps 0.10–0.50 eV) with increasing true lattice conductivity; a matching narrow-gap control with decreasing lattice conductivity; the inherited minority mobility-prefactor sets at ratios 0.1 and 10; the inherited wide-gap upturn set (seed 2004, gaps 1.5–3.55 eV); and two 1,000-curve narrow-gap transfer sets generated from the independent-band rising-channel and independent-band flexible-lattice models and inferred by all six estimators with a common seed of 7300. Pointwise coverage is conditional on scored curves; unscored and admitted counts are reported explicitly. Common-case comparisons use the curves scored by every model, and slope errors use the further subset admitted by every model with finite endpoints."));
T.push(P("On the corpus, each model produces A, B and C as defined in Section 3.2, together with C′_{bip} = B − median κ_{bip} and C′_{all}, which also subtracts median κ_{extra}. Three populations are compared: the *native* set of each model (admission and five positive finite endpoints); the *baseline-common* set, which additionally requires reference admission and finite reference estimates; and the *all-model-common* set, which requires admission and finite estimates in all six models. The paired change subtracts the reference C − B curve by curve on the same population. Intervals use the same 2,000-resample paper-clustered bootstrap and do not integrate over physical-model choice."));

// ---------------- 3. Results ----------------
T.push(H1("3. Results"));
T.push(H2("3.1 Operational fit screen"));
T.push(P(`The corpus contains ${n(V5.n)} eligible, ${n(V5.scored)} scored and ${n(V5.admitted)} admitted curves under the reference model; ${n(V5.paired)} enter the finite paired slope comparison. Admitted curves come from ${n(V5.admitted_papers)} papers.`));
T.push(P(`There are ${n(V5.unscored)} unscored curves and ${n(V5.excluded)} scored exclusions. Low retained-draw counts can reflect prior mismatch or approximation limits; screen failure can reflect observation error or forward-model mismatch. Neither is a diagnosis of multi-band transport.`));
T.push(P("Selection on total containment necessarily increases containment within the admitted group. Table 4 is therefore descriptive, not independent evidence of calibration."));
const pcov = V5.property_coverage;
T.push(TCAP("Table 4.", "Observed-point containment in latent 95% bands, by property and screen category (reference model). These conditional descriptive rates are not calibration estimates."));
T.push(TABLE(["Screen category", "σ", "*S*", "κ"], [
  ["Admitted", ...pcov.admitted.map((x) => x.toFixed(3))],
  ["Excluded", ...pcov.excluded.map((x) => x.toFixed(3))],
], [2, 1, 1, 1]));
T.push(P("Figure 1 reports outcomes by measurement ceiling among scored curves. Bins differ in composition, data quality and window coverage, so rates do not isolate the effect of temperature on physical validity."));
T.push(FIGURE("figure1_fit_screen"));
T.push(CAP("Figure 1.", "Fit-screen outcomes for the reference model. (a) Containment for scored curves and threshold 0.75. (b) Admission fractions among scored curves in measurement-ceiling bins, with 95% paper-clustered bootstrap intervals and bin counts."));

T.push(H2("3.2 Comparison of four lattice estimates"));
T.push(P("We compare A = κ_{meas} − *L*_{Kim}σ_{meas}*T*, B = κ_{meas} − median(*L*_{uni})σ_{meas}*T*, C = median(κ_{L,model}), and C′ = B − median(κ_{bip}). Medians are pointwise over valid draws. A is a retrospective conventional estimate; B changes its Lorenz number; C uses the parametric lattice term; C′ subtracts inferred bipolar heat additively."));
T.push(P("*L*_{uni} = κ_{e,model}/(σ_{model}*T*) excludes bipolar heat and is conductivity-weighted across bands. B applies this coefficient to measured conductivity, whereas the model total uses model conductivity. An effective Lorenz number that includes κ_{bip}/(σ_{model}*T*) is a different convention."));
T.push(P("B − C contains thermal-fit residuals and differences between measured and model conductivity as well as bipolar heat. Sums of marginal posterior medians need not equal the median total. Model-total diagnostics therefore propagate channels using matched parameter draws."));
T.push(P(`C′ compares an additive subtraction on measured total conductivity, but its inferred Lorenz number and bipolar term still depend on the lattice prior. Its median slope is ${ci(V5.slopes.Cp)}; median per-curve shifts are ${ci(V5.shifts.CpB)} relative to B and ${ci(V5.shifts.CpA)} relative to A. Ratios of population medians cannot apportion the C − B shift into mechanistic fractions.`));
T.push(TCAP("Table 5.", `Finite-window log slopes and per-curve differences on ${n(V5.paired)} paired curves (reference model). Intervals resample papers. Medians of differences need not equal differences of medians; successive median shifts need not add.`));
T.push(TABLE(["Estimate or per-curve shift", "Median", "95% interval"], [
  ["A", f(V5.slopes.A[0]), `[${f(V5.slopes.A[1])}, ${f(V5.slopes.A[2])}]`],
  ["B", f(V5.slopes.B[0]), `[${f(V5.slopes.B[1])}, ${f(V5.slopes.B[2])}]`],
  ["C", f(V5.slopes.C[0]), `[${f(V5.slopes.C[1])}, ${f(V5.slopes.C[2])}]`],
  ["C′", f(V5.slopes.Cp[0]), `[${f(V5.slopes.Cp[1])}, ${f(V5.slopes.Cp[2])}]`],
  ...[["B − A", "BA"], ["C − B", "CB"], ["C − A", "CA"], ["C′ − B", "CpB"], ["C′ − A", "CpA"]].map(([l, k]) => [l, f(V5.shifts[k][0]), `[${f(V5.shifts[k][1])}, ${f(V5.shifts[k][2])}]`]),
], [2.2, 1, 1.6]));
const lz = V5.lorenz_change_BminusA_at_Tlo;
T.push(P(`The Lorenz-replacement shift is ${ci(V5.shifts.BA)}; C − B is ${ci(V5.shifts.CB)}. At the lowest measured temperature of each admitted curve, B − A has median ${f(lz[1])} W m^{−1} K^{−1} and 10th–90th percentiles [${f(lz[0])}, ${f(lz[2])}]. The sign follows B − A = (*L*_{Kim} − *L*_{post})σ_{meas}*T*.`));
T.push(P("Different Lorenz prescriptions change A. Agreement with a model slope alone cannot justify a constant Sommerfeld prescription, while disagreement with this model’s Lorenz number does not independently prove over-subtraction. External transport information is needed."));
T.push(P("Inelastic scattering can change the Lorenz number beyond the present power-law relaxation-time model [9]. The corpus comparison does not show that Lorenz uncertainty is unimportant in every material or regime."));

T.push(H2("3.3 Association with inferred bipolar heat"));
const stv = V5.strata;
T.push(P(`The reference-model C − B shift is ${ci(stv.below_2.CB)} below 2% inferred bipolar share, ${ci(stv["2_to_10"].CB)} at 2–10%, and ${ci(stv["10_to_100"].CB)} at 10–100% (Table 6). These are associations within the selected paired population.`));
T.push(TCAP("Table 6.", "Paired-set slopes stratified by posterior median bipolar heat divided by measured total at 750 K (reference model). Both the stratum and the outcome depend on the model; this is an internal association rather than a causal control. Section 3.10 repeats the stratification for all six models."));
T.push(TABLE(["Bipolar share", "n", "B slope", "C slope", "C − B [95% interval]"], [
  ["<2%", stv.below_2], ["2–10%", stv["2_to_10"]], ["10–100%", stv["10_to_100"]],
].map(([l, s]) => [l, n(s.n), f(s.B), f(s.C), ci(s.CB)]).concat([[">100%", "0", "—", "—", "—"]]), [1.2, 0.8, 1, 1, 2]));
T.push(P("There are 0 paired curves with inferred median bipolar heat exceeding measured total, from 0 papers. Absence of such cases does not by itself validate the thermal decomposition."));
T.push(P("Each model draw’s bipolar fraction relative to its own total lies between zero and one because all heat channels are positive. A ratio above one against measured total instead records a discrepancy with the measurement. Matched-draw total and fraction diagnostics are archived, without adding marginal channel medians."));
T.push(P("A low inferred bipolar fraction is not an independent null control. Bias from the lattice form may vary with transport regime; a small shift in one inferred stratum does not bound bias in another."));
T.push(P("C′ separates additive subtraction from replacement by a parametric curve. However, C′ − B is algebraically driven by inferred bipolar heat, so an association with that heat is partly built into the construction and cannot establish lattice-model independence."));
T.push(P(`Across their own windows, ${n(V5.upturn.A.n)} admitted curves (${pc(V5.upturn.A.ci[0])}) have A at the final grid point above A at index 8; B gives ${n(V5.upturn.B.n)} (${pc(V5.upturn.B.ci[0])}). These are two-point upturn indicators, not monotonicity tests. Genuine lattice conductivity can rise, as reported for cubic GeTe [7].`));
T.push(P("The reference model cannot represent a rising lattice term because *w* ≥ 0. Synthetic upturns and flexible-lattice refits are reported in Sections 3.9 and 3.10."));
T.push(FIGURE("figure2_estimates"));
T.push(CAP("Figure 2.", "Reference-model estimates on the paired set. (a) Model-lattice slope shift versus inferred bipolar share, with share defined relative to measured total heat. (b) Model-lattice and additive shifts. (c) Four slope distributions; the displayed range −2 to 1 may omit tails."));

T.push(H2("3.4 Within-family associations"));
const fam = V5.families;
T.push(P(`All ${Object.keys(fam).length} reported reference-model groups have negative median C − B shifts (Table 7; Fig. 3a). Examples are ${ci(fam["half-Heusler"].CB)} for half-Heuslers and ${ci(fam.skutterudite.CB)} for skutterudites. Section 3.11 compares families on identical curves across all six models.`));
const famRows = Object.keys(fam).sort((a, b) => a.localeCompare(b, "en", { sensitivity: "base" })).map((k) => {
  const x = fam[k];
  return [k, n(x.n), f(x.B), f(x.C), ci(x.CB), f(x.rho !== undefined ? x.rho : x.spearman)];
});
T.push(TCAP("Table 7.", `Families with at least 80 paired curves (reference model). ${V5.shared_family_papers} papers contribute to more than one family, so these are not independent replications. Smaller families remain in the overall analysis. Spearman correlations between inferred bipolar share and C − B are descriptive, without cluster-corrected significance tests. Supplementary Table §ST:families§ gives the same comparison for every model.`));
T.push(TABLE(["Family", "n", "B", "C", "C − B [95% interval]", "ρ"], famRows, [1.5, 0.6, 0.8, 0.8, 2, 0.7]));
T.push(P("Family differences may reflect carrier statistics, windows, selection and model adequacy. Chemistry does not guarantee absent minority transport. An interval containing zero is not an equivalence test or proof of no effect."));
T.push(P("Superionic and structurally complex materials stress the transport assumptions. Family labels describe heterogeneity but cannot validate decompositions without additional measurements."));

T.push(H2("3.5 Stratification using measured Seebeck rollover"));
T.push(P("Rollover is the fractional decrease of |*S*| from its interior maximum to the final temperature. Curves without an interior maximum enter the “none” group. The network receives the same *S*(*T*) measurements; the descriptor is input-derived rather than withheld evidence."));
const ro = V5.rollover;
T.push(P("Table 8 and Fig. 3b report the paired-set shifts by rollover; Supplementary Table §ST:rollover§ gives the corresponding results for all models."));
const RK = [["None", "none"], ["<5%", "below_5"], ["5–15%", "5_to_15"], ["≥15%", "above_15"]];
T.push(TCAP("Table 8.", "Paired-set comparisons by measured rollover (reference model). Both B and C depend on the posterior, so the outcome is model-dependent despite the measurement-derived descriptor."));
T.push(TABLE(["Seebeck rollover", "n", "B", "C", "C − B [95% interval]"], RK.map(([l, k]) => [l, n(ro[k].n), f(ro[k].B), f(ro[k].C), ci(ro[k].CB)]), [1.3, 0.8, 1, 1, 2]));
T.push(P("Rollover may be consistent with minority-carrier activation but is not unique to it; it can also be absent when a window ends before the maximum. Agreement supports internal consistency without uniquely establishing a decomposition."));
T.push(P("Table 9 reports the conventional A upturn indicator by measured rollover among all admitted curves. Both descriptors are computable without the simulator, but selection is model-based and *S* enters both rollover and the Kim Lorenz number."));
const ru = V5.rollover_upturn_A;
T.push(TCAP("Table 9.", "Conventional-estimate upturn rates with 95% paper-clustered intervals (reference-model admitted curves). An upturn means A at grid index 15 exceeds A at index 8. It is a signature to explain, not physically impossible lattice conductivity."));
T.push(TABLE(["Seebeck rollover", "n", "A upturn rate [95% interval]"], RK.map(([l, k]) => [l, n(ru[k].n), `${pc(ru[k].ci[0])} [${pc(ru[k].ci[1])}, ${pc(ru[k].ci[2])}]`]), [1.3, 0.8, 2.2]));
T.push(P("These associations do not apportion an upturn between bipolar heat, genuine lattice effects, radiation, measurement error or other mechanisms. Causal interpretation requires evidence beyond the shared inputs."));
T.push(P("These strata partition all admitted curves, not the smaller positive-endpoint paired set. “None” means no interior maximum on the sampled window, rather than absent bipolar transport. External validation would withhold Hall measurements or independently measured gaps and compare predictions against them; that validation has not been performed."));
T.push(P("Cross-classifying thermal upturns and Seebeck rollover does not isolate lattice-prior bias. Both descriptors are related to model inputs, and associations can persist under a biased model. We therefore do not interpret these cross-classifications as a quantitative bound on lattice-model bias; the flexible-lattice refits in Section 3.10 address that question directly within the tested model families. Explicit subset masks and matched draws are released so alternative cross-classifications need not be inferred from rounded table entries."));
T.push(FIGURE("figure3_families_rollover"));
T.push(CAP("Figure 3.", "Reference-model stratifications. (a) Within-family C − B shifts with paper-clustered intervals; family curve counts in parentheses. (b) Shifts by measured rollover. An interval including zero does not establish equivalence; the rollover data were also inputs to inference."));

T.push(H2("3.6 Sensitivity to the fit-screen threshold"));
T.push(P("All scored curves are decomposed. Table 10 varies containment from zero to 0.95, applying the same fixed-window and positive-endpoint rules to all estimates. It describes selection sensitivity without making poorly fitted decompositions reliable."));
const th = V5.thresholds;
T.push(TCAP("Table 10.", "Threshold sensitivity over 400–750 K (reference model). The principal threshold is 0.75. Counts refer to finite paired endpoints at each threshold; only papers represented in each subset are resampled. Supplementary Table §ST:thresholds§ repeats the scan for every model."));
T.push(TABLE(["Threshold", "n", "Papers", "A", "C", "C − B [95% interval]", "C − A"],
  Object.keys(th).map((k) => [k, n(th[k].n), n(th[k].papers), f(th[k].A), f(th[k].C), ci(th[k].CB), f(th[k].CA[0])]), [0.9, 0.7, 0.7, 0.8, 0.8, 2, 0.8]));
T.push(P("The scan should be assessed alongside changes in population and fit quality. Stability across thresholds addresses this selection choice but does not remove misspecification, prior dependence or approximation error."));
T.push(P("Non-positive endpoints have no real logarithmic slope and are explicitly excluded, not clipped to 10^{−6}. Negative subtraction values remain in the archive for diagnostics. Positive model lattice heat is guaranteed by the prior, rather than evidence of a correct decomposition."));

T.push(H2("3.7 Effective scattering exponent across the corpus"));
const cl = V5.classes;
T.push(P(`The median posterior effective *r* among admitted curves is ${ci(V5.r_median)}. *P*(*r* < 0.5) uses finite retained draws only; missing draws do not count as evidence above the threshold.`));
T.push(P(`Class fractions are ${pc(cl.phonon_like.fraction)} phonon-like, ${pc(cl.impurity_like.fraction)} impurity-like and ${pc(cl.ambiguous.fraction)} ambiguous, using probabilities above 0.8, below 0.2 and between them. These effective-parameter labels do not independently identify microscopic mechanisms.`));
T.push(P("These are effective scattering exponents conditional on the forward model and the prior, not microscopic mechanisms established independently. A single *r* stands in for whatever combination of acoustic, polar-optical, alloy and ionised-impurity scattering a sample exhibits, and mixed scattering, band complexity or the sharing of *r* between electrons and holes can reproduce an intermediate value with no single mechanism dominating. The classes describe what three transport curves determine about an effective exponent, and are assigned per curve rather than per material: several curves from one study may share a composition. When the bands are given separate exponents, the minority exponent is ambiguous for most admitted curves (Supplementary Table §ST:scattering§)."));
T.push(FIGURE("figure4_scattering"));
T.push(CAP("Figure 4.", "Effective scattering exponent among reference-model admitted curves. (a) Posterior medians by probability class, with *r* = −1/2 and +3/2 reference lines. (b) Class fractions and paper-clustered intervals. Counts refer to curves, not distinct materials."));
T.push(P("Mobility contains both a temperature prefactor and a Fermi-integral ratio. In the strongly degenerate fixed-density limit, η ∝ *T*^{−1} and mobility varies as temperature raised to *p*_{μ} − *r*, rather than *p*_{μ} alone. This helps explain an *r*–*p*_{μ} trade-off. Activation supplies a different temperature shape, but improved identification requires empirical diagnostics."));

T.push(H2("3.8 Non-positive conventional remainders"));
const na = V5.negative_A;
T.push(P(`Negative A indicates incompatibility between measured inputs and the chosen subtraction, rather than negative physical lattice conductivity. Counts are reported separately for the full corpus, admitted curves, scored exclusions and unscored curves: ${na.all.n}/${n(na.all.denominator)} overall, ${na.admitted.n}/${n(na.admitted.denominator)} admitted, ${na.excluded.n}/${n(na.excluded.denominator)} excluded and ${na.unscored.n}/${n(na.unscored.denominator)} unscored. The corresponding counts for each extended model are in Supplementary Table §ST:selection§.`));
T.push(P("A threshold such as 0.15 W m^{−1} K^{−1} is a diagnostic scale, not a universal lower physical bound. Non-negative C follows from the prior and neither repairs incompatible measurements nor verifies a decomposition."));

// ---------------- 3.9 synthetic ----------------
T.push(H2("3.9 Relaxing carrier symmetry and lattice monotonicity: known-truth tests"));
T.push(P(`On their own independent test sets, the five extended estimators score ${n(Math.min(...VAR.map((m) => same[m].scored)))}–${n(Math.max(...VAR.map((m) => same[m].scored)))} of 6,000 curves, with nominal 95% pointwise lattice coverage of ${pcn(Math.min(...sameCov))}–${pc(Math.max(...sameCov))} and bipolar coverage of ${pcn(Math.min(...VAR.map((m) => same[m].bipolar_coverage)))}–${pc(Math.max(...VAR.map((m) => same[m].bipolar_coverage)))} (Supplementary Table §ST:same§). All fall below the nominal level, so successful training does not establish calibration even when the test distribution matches the prior.`));
const ub = nu.baseline, us = nu.mobility_spline, usp = nu.spline;
T.push(P(`The narrow-gap upturn set tests the reference model’s monotone-lattice restriction directly. The reference model scores ${ub.scored} of 1,000 curves and admits ${ub.admitted}; its lattice coverage is ${pc(ub.lattice_coverage)} and bipolar coverage ${pc(ub.bipolar_coverage)}, and on ${ub.slope_n} admitted curves with finite endpoints the median C slope is ${f(Math.abs(ub.median_slope_error))} below the true lattice slope. Models whose lattice remains monotone behave similarly (lattice coverage ${pcn(Math.min(nu.mobility.lattice_coverage, nu.extra.lattice_coverage, nu.mobility_extra.lattice_coverage))}–${pc(Math.max(nu.mobility.lattice_coverage, nu.extra.lattice_coverage, nu.mobility_extra.lattice_coverage))}). A rising total can be represented by the extra channel without being assigned to the correct physical channel. The flexible-lattice models score ${usp.scored} (shared bands) and ${us.scored} (independent bands) curves, with lattice coverage ${pc(usp.lattice_coverage)} and ${pc(us.lattice_coverage)} (Supplementary Table §ST:narrowNative§).`));
T.push(P(`These native comparisons change their denominators across models. On the ${up.common_scored_n} upturn curves scored by all six models (Fig. 5a–c, Supplementary Table §ST:commonUpturn§), independent-band flexible-lattice inference raises lattice coverage from ${pc(up.models.baseline.lattice_coverage)} to ${pc(up.models.mobility_spline.lattice_coverage)}, but its median lattice interval widens from ${f(up.models.baseline.lattice_width)} to ${f(up.models.mobility_spline.lattice_width)} W m^{−1} K^{−1}; the shared-band flexible model reaches ${pc(up.models.spline.lattice_coverage)} with a width of ${f(up.models.spline.lattice_width)} W m^{−1} K^{−1}. On the further ${up.common_slope_n} curves admitted by every model, the median absolute slope error changes from ${f(up.models.baseline.common_slope.median_absolute_error)} to ${f(up.models.mobility_spline.common_slope.median_absolute_error)}; the shared-band flexible model gives ${f(up.models.spline.common_slope.median_absolute_error)}. Higher coverage is therefore bought with width, not with more accurate point estimates on fixed cases. The much smaller signed error in the model-specific subset (${f(us.median_slope_error)} on ${us.slope_n} curves) must not be read as an improvement of that size.`));
const wu = sc.wide_upturn;
T.push(P(`The inherited wide-gap upturn set (gaps 1.5–3.55 eV), where bipolar heat is small, shows the same trade-off on a smaller common population. Only ${wu.common_scored_n} of its 1,000 curves are scored by every model; flexible lattices raise lattice coverage from ${pc(wu.models.baseline.lattice_coverage)} to ${pc(wu.models.spline.lattice_coverage)} (shared bands) and ${pc(wu.models.mobility_spline.lattice_coverage)} (independent bands), while median absolute slope error on the ${wu.common_slope_n} curves admitted by all models is ${f(wu.models.spline.common_slope.median_absolute_error)} and ${f(wu.models.mobility_spline.common_slope.median_absolute_error)}, against ${f(wu.models.baseline.common_slope.median_absolute_error)} for the reference model (Supplementary Table §ST:wide§).`));
const ml = sc.mobility_low, mh = sc.mobility_high;
T.push(P(`The mobility-prefactor stress sets isolate the carrier-symmetry restriction. On ${ml.common_scored_n} and ${mh.common_scored_n} commonly scored curves at minority ratios 0.1 and 10, bipolar coverage rises from ${pc(ml.models.baseline.bipolar_coverage)} and ${pc(mh.models.baseline.bipolar_coverage)} in the reference model to ${pc(ml.models.mobility.bipolar_coverage)} and ${pc(mh.models.mobility.bipolar_coverage)} with independent bands, while lattice coverage in these two models stays between ${pcn(Math.min(ml.models.baseline.lattice_coverage, mh.models.baseline.lattice_coverage))}% and ${pc(Math.max(ml.models.mobility.lattice_coverage, mh.models.mobility.lattice_coverage))} (Supplementary Table §ST:mobility§). These tests vary a prefactor only; they do not exhaust temperature-exponent, scattering-law or band-shape departures.`));
const t1 = tx["mobility_spline|mobility_extra"], t2 = tx["mobility_extra|mobility_spline"], t0 = tx["baseline|mobility_spline"];
T.push(P(`Transfer between thermal hypotheses probes attribution when the assumed family is wrong (Fig. 5d, Supplementary Table §ST:transfer§). Applied to rising-channel truth, the independent-band flexible-lattice estimator scores ${t1.scored} of 1,000 curves and reaches ${pc(t1.lattice_coverage)} lattice coverage despite ${pc(t1.total_coverage)} total-conductivity coverage: the total is reproduced while heat is partly mis-assigned. In the reverse direction the independent-band rising-channel estimator scores only ${t2.scored} curves, with ${pc(t2.lattice_coverage)} lattice coverage, and the reference model scores ${t0.scored} with ${pc(t0.lattice_coverage)}. Agreement with the measured total therefore does not identify the thermal family. Neither transfer set says which family is present in experimental specimens.`));
T.push(P(`The decreasing-lattice narrow-gap control shows the converse effect. Of ${ctl.admitted} curves admitted by the reference model, ${ctl.apparent_upturn_admitted} (${pc(ctl.apparent_upturn_admitted / ctl.admitted)}) show an apparent upturn in the conventional estimate A although no true lattice curve rises (${ctl.true_lattice_upturn_admitted} of ${ctl.admitted}); the median true bipolar share at the upper window edge is ${f(ctl.median_true_bipolar_fraction_at_Thi_upturn, 2)} in those curves and ${f(ctl.median_true_bipolar_fraction_at_Thi_other, 3)} in the rest. On the ${sc.narrow_control.common_scored_n} control curves scored by all models, lattice coverage is ${pcn(Math.min(...M.map((m) => sc.narrow_control.models[m].lattice_coverage)))}–${pc(Math.max(...M.map((m) => sc.narrow_control.models[m].lattice_coverage)))} (Supplementary Table §ST:control§). Within the simulator, apparent conventional upturns therefore arise without any lattice upturn and coincide with large bipolar shares, although A also inherits any error of the Kim Lorenz estimate. This does not bound the prevalence of the mechanism in the corpus.`));
T.push(FIGURE("figure5_synthetic_tests"));
T.push(CAP("Figure 5.", `Known-truth tests of the six models. (a–c) Narrow-gap curves with rising true lattice conductivity: nominal 95% pointwise lattice coverage and median interval width on the ${up.common_scored_n} curves scored by all models (b, log scale), and median absolute 400–750 K lattice-slope error on the ${up.common_slope_n} curves admitted by all models with finite endpoints. (d) Lattice coverage when every model infers 1,000 curves generated from independent-band rising-channel or independent-band flexible-lattice truth; denominators are each model’s scored curves and differ between bars. Dashed lines mark 95%. Panels a–c use the inherited development benchmark; panel d uses independently generated transfer sets. Bars show descriptive point estimates, not uncertainty intervals.`));

// ---------------- 3.10 corpus robustness ----------------
T.push(H2("3.10 Corpus robustness across six models"));
T.push(P(`Every model reconstructs B, C and both additive estimates from its own posterior outputs; none is copied from the reference model. On identical measured curves A is invariant. For flexible-lattice models, C is the pointwise posterior median of the PCHIP lattice function. C′_{bip} instead uses that model’s B and bipolar median; the PCHIP hypothesis affects this additive estimate indirectly through joint inference. C′_{all} further subtracts the extra-channel median in rising-channel models and otherwise equals C′_{bip}.`));
T.push(P(`Supplementary Table 28 reports all five component slope medians on the same ${n(X.n)} curves from ${n(X.papers)} papers, and Supplementary Table 29 reports their paired differences. Reference, flexible-lattice and independent-band flexible-lattice median C slopes are ${f(X.models.baseline.slopes.C[0])}, ${f(X.models.spline.slopes.C[0])} and ${f(X.models.mobility_spline.slopes.C[0])}; their additive C′_{bip} slopes are ${f(X.models.baseline.slopes.Cprime_bip[0])}, ${f(X.models.spline.slopes.Cprime_bip[0])} and ${f(X.models.mobility_spline.slopes.Cprime_bip[0])}. C and C′ need not coincide because measured and fitted transport differ and marginal medians are not additive.`));
T.push(P(`Paired changes from the reference model distinguish movement in B from movement in C (Supplementary Table 30). For the flexible-lattice model, the median changes are ${ci(X.models.spline.changes_from_reference.B)} in B and ${ci(X.models.spline.changes_from_reference.C)} in C. With independent bands and a flexible lattice, they are ${ci(X.models.mobility_spline.changes_from_reference.B)} and ${ci(X.models.mobility_spline.changes_from_reference.C)}, respectively. The larger typical movement is therefore in the directly inferred lattice slope. This descriptive comparison does not isolate a causal lattice, bipolar or Lorenz contribution: all posterior quantities are jointly inferred. Changes in C − B are computed per curve, not by subtracting these population medians.`));
T.push(P(`The extended models change which curves are analysed. They admit ${n(Math.min(...adm))}–${n(Math.max(...adm))} curves, against ${n(V5.admitted)} for the reference model, and their native paired sets contain ${n(Math.min(...nat))}–${n(Math.max(...nat))} curves (Supplementary Table §ST:selection§). Wider posterior bands raise containment, so additional admitted curves are not additional accurately decomposed specimens, and native comparisons mix changed inference with changed selection.`));
T.push(P(`Table 11 and Fig. 6a therefore also report the ${n(common.n)} curves from ${n(common.papers)} papers that every model admits with finite endpoints. On this fixed population, the median C − B shift is negative in all six models and every interval excludes zero, ranging from ${ci(cb("baseline"))} for the reference model to ${ci(cb("mobility_spline"))} for independent bands with a flexible lattice; C − A ranges from ${f(ca("baseline")[0])} to ${f(ca("mobility_spline")[0])}. The paired change relative to the reference model is small when only carrier symmetry is relaxed (${ci(C.mobility.all_model_common.paired_change_CB)}) and largest when the lattice is flexible (${ci(C.spline.all_model_common.paired_change_CB)} with shared bands; ${ci(C.mobility_spline.all_model_common.paired_change_CB)} with independent bands). Relaxing carrier symmetry alone therefore changes little, a flexible lattice changes the shift most, and the two interact: adding independent bands to a flexible lattice nearly doubles the paired change. The interaction depends on the population, since on native sets the shared-band flexible model gives the larger shift (${f(C.spline.native.CB[0])} versus ${f(C.mobility_spline.native.CB[0])}).`));
T.push(TCAP("Table 11.", `Median per-curve C − B and C − A slope shifts over 400–750 K for each model. Native sets differ between models; the all-model-common set contains the same ${n(common.n)} curves from ${n(common.papers)} papers for every model. Paired change is the median of the per-curve difference from the reference model’s C − B on the common set. Brackets are 95% paper-clustered bootstrap intervals; they do not include uncertainty over model choice. Baseline-common results are in Supplementary Table §ST:populations§.`));
T.push(TABLE(["Model", "Native n", "Native C − B", "Common C − B", "Common C − A", "Paired change"],
  M.map((m) => [SH[m], n(C[m].native.n), ciB(C[m].native.CB), ciB(cb(m)), ciB(ca(m)), m === "baseline" ? "0 (reference)" : ciB(C[m].all_model_common.paired_change_CB)]),
  [1.55, 0.75, 1.75, 1.75, 1.75, 1.75]));
const st_ = N.strata, rl = N.rollover;
const rollMono = M.filter((m) => { const v = RK.map(([, k]) => rl[m][k].CB[0]); return v.every((x, q) => q === 0 || x < v[q - 1]); });
if (!M.every((m) => rl[m].above_15.CB[0] < rl[m].none.CB[0])) throw new Error("rollover claim: ≥15% not below none in some model");
if (rl.spline.below_5.CB[0] > rl.spline.above_15.CB[0] || rl.mobility_spline.below_5.CB[0] > rl.mobility_spline.above_15.CB[0]) throw new Error("flexible rollover claim changed");
if (!M.every((m) => ["below_2", "2_to_10"].every((k) => st_[m]["10_to_100"].CB[0] < st_[m][k].CB[0]))) throw new Error("top-stratum claim changed");
if (!M.every((m) => cb(m)[2] < 0)) throw new Error("common-set interval includes zero");
const thrMonoMax = Math.max(...["baseline", "mobility", "extra", "mobility_extra"].map((m) => N.threshold_range_CB[m][1] - N.threshold_range_CB[m][0]));
T.push(P(`The association with inferred bipolar heat persists under every model (Table 12, Fig. 6b; detailed counts and intervals in Supplementary Table §ST:strata§). In each model the 10–100% bipolar-share stratum has the most negative shift, ${Math.min(...ratios).toFixed(1)}–${Math.max(...ratios).toFixed(1)} times that of the <2% stratum. The ordering of the two lower strata is not preserved in the independent-band flexible-lattice model (${f(st_.mobility_spline.below_2.CB[0])} below 2% versus ${f(st_.mobility_spline["2_to_10"].CB[0])} at 2–10%; point estimates with overlapping intervals), which assigns larger shifts to some low-bipolar curves. Both stratum and outcome are model-dependent, so this persistence is internal consistency rather than independent confirmation.`));
T.push(P(`Stratification by measured Seebeck rollover is less uniform (Table 12, Fig. 6c). In every model the ≥15% group has a more negative shift than curves without an interior maximum, and the shift grows monotonically with rollover in the ${rollMono.map((m) => SH[m].toLowerCase()).join(", ").replace(/, ([^,]*)$/, " and $1")} model${rollMono.length > 1 ? "s" : ""}. In the independent + rising model the two intermediate groups are nearly equal (${f(rl.mobility_extra.below_5.CB[0])} and ${f(rl.mobility_extra["5_to_15"].CB[0])}), and in both flexible-lattice models the largest shift falls in the <5% group (${f(rl.spline.below_5.CB[0])} and ${f(rl.mobility_spline.below_5.CB[0])}) rather than at ≥15%. Across families, all ${famCells.length} model–family medians with at least 80 curves, including the residual “other” groups, are negative, and ${famCells.length - famIncl0.length} of their intervals exclude zero; the exception is ${famIncl0.map((x) => `${x.k} under the ${SH[x.m].toLowerCase()} model (${ci(x.v.CB)}, n = ${x.v.n})`).join("; ")} (Supplementary Table §ST:families§). Varying the fit-screen threshold from 0 to 0.95 moves C − B by at most ${thrMonoMax.toFixed(3)} in the four models with a monotone lattice and by ${(N.threshold_range_CB.mobility_spline[1] - N.threshold_range_CB.mobility_spline[0]).toFixed(3)} in the independent + flexible model; in the shared-band flexible lattice it ranges from ${f(thrSpline[0])} to ${f(thrSpline[1])} (Supplementary Table §ST:thresholds§).`));
T.push(TCAP("Table 12.", "Median C − B slope shift by inferred bipolar share at 750 K and by measured Seebeck rollover, native paired set of each model. Counts and 95% paper-clustered intervals are in Supplementary Tables §ST:strata§ and §ST:rollover§. The bipolar stratum is defined by each model’s own posterior median bipolar heat divided by measured total. Columns 2–4 give inferred bipolar share; columns 5–8 give measured Seebeck rollover."));
T.push(TABLE(["Model", "<2%", "2–10%", "10–100%", "None", "<5%", "5–15%", "≥15%"],
  M.map((m) => [SH[m], ...["below_2", "2_to_10", "10_to_100"].map((k) => f(st_[m][k].CB[0])), ...RK.map(([, k]) => f(rl[m][k].CB[0]))]),
  [1.9, 0.8, 0.8, 0.9, 0.8, 0.8, 0.8, 0.8]));
T.push(FIGURE("figure6_model_robustness"));
T.push(CAP("Figure 6.", `Model dependence of the corpus comparison. (a) Median per-curve C − B and C − A slope shifts on the ${n(common.n)} curves from ${n(common.papers)} papers selected by all six models. (b) C − B by inferred bipolar share at 750 K and (c) by measured Seebeck rollover, each on the native paired set of that model. Horizontal bars are 95% paper-clustered bootstrap intervals (2,000 resamples); they do not include uncertainty over physical-model choice. Dashed lines mark zero shift.`));

const FC = N.family_common;
T.push(H2("3.11 Family comparisons on identical experimental curves"));
T.push(P(`Native family tables describe different selected populations. We also compare each family on the intersection of admission and finite 400–750 K endpoints across all six models (Fig. 7; Supplementary Tables 26 and 27). Effects are reported for groups with at least 80 curves. Four named groups meet this threshold: ${["Mg2X-type","filled-RE","half-Heusler","skutterudite"].map(k => `${k} (${n(FC.families[k].n)} curves, ${n(FC.families[k].papers)} papers)`).join(", ")}. The heterogeneous residual other group contains ${n(FC.families.other.n)} curves from ${n(FC.families.other.papers)} papers and is shown separately. Family names are inherited labels, not newly verified phase or composition assignments.`));
T.push(P(`For half-Heuslers, the common-family median C − B is ${ci(FC.families["half-Heusler"].models.baseline.C_B)} in the reference model and ${ci(FC.families["half-Heusler"].models.mobility_spline.C_B)} with independent bands and a flexible lattice. The paired median change is ${ci(FC.families["half-Heusler"].models.mobility_spline.paired_change_from_reference)}. Corresponding skutterudite shifts are ${ci(FC.families.skutterudite.models.baseline.C_B)} and ${ci(FC.families.skutterudite.models.mobility_spline.C_B)}. Thus substantial family-specific model dependence persists on the same curves; these changes are not independently measured corrections.`));
T.push(P("The nine other family labels have fewer than 80 common curves and are retained in the overall analysis; their counts are listed without ranked effect estimates in Supplementary Table 26. In particular, PbX-type, Cu2Se-type, SiGe and SnSe-type are represented in native tables but do not meet this common-set threshold. Family-conditioned bootstrap intervals use source-paper clusters and are not adjusted for multiple comparisons. Overlapping papers and inherited family labels preclude treating families as independent validation experiments."));
T.push(FIGURE("figure7_common_families"));
T.push(CAP("Figure 7.", "Family-conditioned model comparisons on identical curves. Points show median C − B log-slope shifts over 400–750 K; intervals are 95% percentile intervals from 2,000 source-paper bootstrap resamples. Every model uses the same curves within each displayed group. Labels give curves and papers. Only groups with at least 80 common curves are plotted; other is a heterogeneous residual group. The vertical dashed line marks zero. These descriptive intervals quantify paper-sampling variation within the selected groups, not model-choice uncertainty or independently verified channel truth."));

// ---------------- 4. Discussion ----------------
T.push(H1("4. Discussion"));
T.push(P("Under a unipolar convention, bipolar heat remains in κ − *L*σ*T*. This comparison quantifies how specified models partition that remainder and change finite-window slopes; it does not establish bipolar heat as the only explanation."));
T.push(P("One scoping point governs what follows. We apply a standard recipe to published σ, *S* and κ; we do not read each source publication to establish whether its authors used that recipe, applied a bipolar correction, or reported κ_{L} + κ_{bip} knowingly. The claim is about what the conventional recipe yields across the published record, not that any particular reported value is wrong."));
T.push(P(`The six-model comparison separates two claims that a single model cannot. On a fixed population of ${n(common.n)} curves, the sign of the median shift, a more steeply falling model lattice estimate relative to the unipolar remainder, survives relaxation of carrier symmetry and of lattice monotonicity. On each model’s native set the shift is also largest in the highest inferred-bipolar stratum and larger at ≥15% rollover than without rollover, although the rollover gradient is not monotone in the flexible-lattice models. The size of the shift does not survive: the common-set median varies about ${(cb("mobility_spline")[0] / cb("baseline")[0]).toFixed(1)}-fold between models, with the largest changes when the lattice is flexible, particularly together with independent bands. Under these models, part of the conventional high-temperature remainder in bipolar-prone curves is attributed to bipolar heat, flattening its decline. That qualitative statement is better supported than any single numerical correction, and it remains a model attribution rather than a measured error.`));
T.push(P("The known-truth tests show why the magnitude stays uncertain. Restricting the lattice to decrease produces confident but wrong lattice slopes when the truth rises; freeing it increases coverage to near or above the nominal target by widening intervals roughly nine- to fourteen-fold without reducing median absolute slope error, and estimators fitted under one thermal hypothesis mis-assign heat generated under another while still reproducing the measured total. Three transport curves do not, by themselves, identify how high-temperature heat is shared between lattice, bipolar and other channels. Flexibility exposes this non-identifiability; it does not resolve it."));
T.push(P("The comparisons do not compute model probabilities or a model-averaged decomposition, and the alternatives differ in dimension and prior support as well as in physics. Lattice and bipolar coverage below nominal in the same-model tests, larger draw-to-draw spread in flexible models, and the Gaussian approximation all remain part of the interpretation. Wider posterior bands also raise the containment-based admission rate, so selection must be controlled, as here, before attributing a change to the physical decomposition."));
T.push(P("Genuine lattice upturns, radiation, sample changes, band complexity and imperfect error models challenge inference. Associations with inferred bipolar heat and measured rollover remain descriptive evidence, not independent validation. Joint modelling exposes assumptions and tests agreement with several measured channels, at the cost of dependence on the full simulator, prior and approximation. Reproducibility is necessary for assessing these dependencies but insufficient for physical validation."));

// ---------------- 5. Limitations ----------------
T.push(H1("5. Limitations"));
T.push(P("The fit screen neither establishes calibration on real materials nor diagnoses exclusions. Publication, digitisation and historical selection effects also limit generalisation beyond this corpus."));
T.push(P("Bootstrap intervals describe paper-sampling variation within selected subsets, not systematic measurement errors, uncertainty in the lost historical filter, all posterior approximation errors or choice of physical model."));
T.push(P("Carrier-asymmetry tests on the reference model generate 1,000 curves each at minority mobility multipliers 0.1 and 10 (seeds 2005 and 2006), then infer them using the shared-mobility model. These rates use each set’s native scored curves; Section 3.9 reports the sets scored by all six models. For multiplier 0.1, 841 curves were scored and 765 admitted; κ_{L} and κ_{bip} pointwise coverage on scored curves was 90.9% and 73.6%. For multiplier 10, 696 curves were scored and 595 admitted; κ_{L} and κ_{bip} pointwise coverage on scored curves was 89.6% and 71.5%. The independent-band models address this departure (Section 3.9) but not unequal band shapes or non-parabolic dispersion."));
T.push(P("A separate 1,000-curve test (seed 2004) generates increasing lattice heat with *w* between −1.2 and −0.2 and gaps from 1.5 to approximately 3.55 eV, then infers with *w* ≥ 0. Where true bipolar heat is below 2% of true total at *T*_{hi}, a false assignment means an inferred median above 10% of that total. False assignments occurred in 13 of 214 eligible scored cases and 12 of 160 eligible admitted cases. All six models were also run on this set (Section 3.9)."));
T.push(P("The flexible lattice depends on six fixed knots and a broad independent node prior whose support was widened after inspection of the inherited benchmarks; knot placement and node-prior alternatives have not been tested. The rising channel has one fixed cubic shape and a bounded amplitude. Each extended model was trained with a single seed, and all use the same Gaussian density head and sign factorisation. Non-parabolic and multi-valley bands, specimen-dependent measurement errors and correlated calibration errors are not represented."));
T.push(P("The inferred gap is not an independently validated measurement. Goldsmid–Sharp estimates [6] reuse Seebeck data already seen by the network. Gap and minority mass affect bipolar transport, so their uncertainty or bias can propagate into κ_{L}; the lattice result is not independent of them."));
T.push(P("Multiplicative 2% noise preserves the sign of *S* and has vanishing absolute error near zero. It induces interpolation correlations but omits shared systematics and additive error. Larger digitisation or measurement errors affect screening and uncertainty interpretation."));

// ---------------- 6. Remaining validation ----------------
T.push(H1("6. Remaining validation needs"));
T.push(P("This work corrects the implementation, adds independent synthetic diagnostics and refits the corpus under five relaxed models. Open scientific limitations are distinguished from completed checks."));
T.push(P("Flexible-lattice models have now been fitted to real curves and known-truth simulations. Their sensitivity to knot placement, node priors and alternative positive lattice families remains to be tested, and model probabilities or model averaging over the six hypotheses have not been computed."));
T.push(P("Further checks should examine joint rank calibration, simultaneous coverage, more flexible conditional density estimators, replicate training seeds, per-curve MCMC comparisons and larger draw counts. Carrier tests should vary band shape and non-parabolicity. The current tests cover selected departures rather than every plausible mismatch."));
T.push(P("External benchmarks should use matched specimens with Hall data, independent gaps or thermal-separation experiments. Model-assisted decompositions [10,11] and low-temperature high-field separation [9] are informative comparisons, but should not be treated as direct high-temperature ground truth without examining assumptions. Such constraints are the most direct route to narrowing the model dependence documented here."));
T.push(P("A source-paper audit must record which quantity and correction each publication reported before claiming errors in published lattice values. It was not performed here. These decomposition choices do not change measured *zT* = *S*^{2}σ*T*/κ; they change its interpretation."));

// ---------------- availability ----------------
T.push(H1("Code availability"));
T.push(P("The accompanying GitHub source archive contains the reference and extended forward models, explicit priors and observation simulator, training and inference commands, the reference checkpoint and five extended checkpoints with training histories, numerical summaries, figures and checksums. Large frozen observations, matched draws, independent validation and stress arrays, and cross-model transfer arrays are provided in the separate research-data archive, not in the GitHub source archive. Extended-model runs are stored under runs/v6_main. The combined/ directory rebuilds the manuscript tables and figures from archived outputs (build_combined_numbers.py, make_combined_figures.py) and checks numerical-token traceability (verify_combined_manuscript.py). That token check is supplemented by claim-specific and common-family checks; numerical-token matching alone does not verify context or interpretation. Training sets are regenerated from their seeds. Device and floating-point variation may prevent bitwise equality of retraining; archived arrays and checkpoints define the reported results."));
T.push(H1("Data availability"));
T.push(P(`Source measurements are from Starrydata [5]. The analysed sample list identifies ${n(V5.n)} records from ${n(V5.papers)} papers. The official per-project files are pinned to https://github.com/starrydata/starrydata_datasets/releases/tag/data-20261008, whose manifest reports database snapshot 9 October 2026. Source hashes, DOI/sample identities, final-row mappings, retained posterior arrays and analysis summaries accompany the code and separate data archive. A public versioned code repository and persistent data-deposit identifiers will be supplied by the authors before publication.`));

// ---------------- references ----------------
T.push(H1("References"));
const REFS = [
  "Kim, H.-S., Gibbs, Z. M., Tang, Y., Wang, H. & Snyder, G. J. Characterization of Lorenz number with Seebeck coefficient measurement. *APL Materials* 3, 041506 (2015). doi:10.1063/1.4908244",
  "Papamakarios, G. & Murray, I. Fast ε-free inference of simulation models with Bayesian conditional density estimation. *Advances in Neural Information Processing Systems* 29 (2016).",
  "Cranmer, K., Brehmer, J. & Louppe, G. The frontier of simulation-based inference. *PNAS* 117, 30055–30062 (2020). doi:10.1073/pnas.1912789117",
  "Talts, S., Betancourt, M., Simpson, D., Vehtari, A. & Gelman, A. Validating Bayesian inference algorithms with simulation-based calibration. arXiv:1804.06788 (2018).",
  "Katsura, Y., Kumagai, M., Mato, T., Takada, Y., Ando, Y., Fujita, E., Hosono, F., Koyama, E., Mudasar, F., Phuong, T. N. T., Saito, N., Sakamoto, Y., Tanaka, A., Yana, D., Kimura, K., Tsuda, K. & Demura, M. Starrydata: from published plots to shared materials data. *Science and Technology of Advanced Materials: Methods* 5, 2506976 (2025). doi:10.1080/27660400.2025.2506976",
  "Goldsmid, H. J. & Sharp, J. W. Estimation of the thermal band gap of a semiconductor from Seebeck measurements. *Journal of Electronic Materials* 28, 869–872 (1999). doi:10.1007/s11664-999-0211-y",
  "Kielar, S., Li, C., Huang, H., Hu, R., Slebodnick, C., Alatas, A. & Tian, Z. Anomalous lattice thermal conductivity increase with temperature in cubic GeTe correlated with strengthening of second-nearest neighbor bonds. *Nature Communications* 15, 6981 (2024). doi:10.1038/s41467-024-51377-8",
  "Kuo, J. J., Wood, M., Slade, T. J., Kanatzidis, M. G. & Snyder, G. J. Systematic over-estimation of lattice thermal conductivity in materials with electrically-resistive grain boundaries. *Energy & Environmental Science* 13, 1250–1258 (2020). doi:10.1039/C9EE03921J",
  "Candolfi, C., Wiendlocha, B., Ohorodniichuk, V., Levinský, P., Migot, S., Steciuk, G., Terzi, I., Wieder, A., Dauscher, A., El Oualid, S. & Lenoir, B. Hidden in plain heat: anomalous Lorenz number in the thermoelectric alloy Bi_{0.4}Sb_{1.6}Te_{3}. *Nature Communications* 16, 11528 (2025). doi:10.1038/s41467-025-66578-y",
  "Kim, H.-S., Lee, K. H., Yoo, J., Youn, J., Roh, J. W., Kim, S.-i. & Kim, S. W. Effect of substitutional Pb doping on bipolar and lattice thermal conductivity in p-type Bi_{0.48}Sb_{1.52}Te_{3}. *Materials* 10, 763 (2017). doi:10.3390/ma10070763",
  "Wang, S., Yang, J., Toll, T., Yang, J., Zhang, W. & Tang, X. Conductivity-limiting bipolar thermal conductivity in semiconductors. *Scientific Reports* 5, 10136 (2015). doi:10.1038/srep10136",
  "Fritsch, F. N. & Butland, J. A method for constructing local monotone piecewise cubic interpolants. *SIAM Journal on Scientific and Statistical Computing* 5, 300–304 (1984). doi:10.1137/0905021",
];
REFS.forEach((ref, i) => T.push(new Paragraph({ spacing: { after: 80, line: 260 }, indent: { left: 440, hanging: 440 }, children: [new TextRun({ text: `[${i + 1}]\t`, size: 20 }), ...runs(ref, { size: 20 })], tabStops: [{ type: "left", position: 440 }] })));

// =====================================================================================
// SUPPLEMENTARY INFORMATION
// Supplementary tables are numbered in order of first citation in the main text
// (st() assigns numbers as the main text is built); uncited tables follow in list order.
// =====================================================================================
const S = [];
S.push(new Paragraph({ style: "Title", children: [new TextRun("Supplementary Information")] }));
S.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 300 }, children: [new TextRun({ text: "Bipolar heat and model-dependent estimates of lattice thermal conductivity across a thermoelectric corpus", italics: true })] }));
S.push(P("This Supplementary Information accompanies the main manuscript and provides detailed training records, validation results, sensitivity analyses and family comparisons. It uses the model definitions and statistical conventions specified in the main Methods."));
S.push(P("Model names follow Section 2.7 of the main text: Reference (shared bands, monotone lattice), Independent bands, Rising channel, Flexible lattice, Independent + rising and Independent + flexible. Coverage values are nominal 95% pointwise coverage conditional on scored curves. Native populations differ between models; common-case comparisons use explicit intersections. Brackets are 95% paper-clustered bootstrap intervals (2,000 resamples). Numerical tables are assembled from the archived analysis summaries. The companion code records their provenance and reconstruction commands."));

const VR = VAR;
const SKEYS = [["<2%", "below_2"], ["2–10%", "2_to_10"], ["10–100%", "10_to_100"]];
const TH = Object.keys(N.thresholds.baseline);
const nc = sc.narrow_control;
const SI = {
  same: () => [TCAP(`Supplementary Table ${st("same")}.`, "Independent same-model tests (6,000 curves per extended model, drawn from that model’s prior)."),
    TABLE(["Model", "Scored / generated", "Admitted", "Lattice coverage (%)", "Bipolar coverage (%)", "Lattice median abs. relative error"],
      VR.map((m) => [SH[m], `${n(same[m].scored)}/${n(same[m].n)}`, n(same[m].admitted), pcn(same[m].lattice_coverage), pcn(same[m].bipolar_coverage), same[m].lattice_median_abs_rel_error.toFixed(3)]), [1.8, 1.2, 0.9, 1, 1, 1.2]),
    NOTE("Reference-model results on its own 6,000-curve test set are in main-text Section 2.5. Relative errors exclude truth values at or below 10^{−12}.")],
  narrowNative: () => [TCAP(`Supplementary Table ${st("narrowNative")}.`, "Native narrow-gap lattice-upturn evaluation (1,000 curves, gaps 0.10–0.50 eV, increasing true lattice conductivity). The slope error is the median model C slope minus true lattice slope over 400–750 K on admitted curves with finite endpoints; its denominator changes between models."),
    TABLE(["Model", "Scored", "Admitted", "Lattice coverage (%)", "Bipolar coverage (%)", "Slope subset n", "Median slope error"],
      M.map((m) => [SH[m], n(nu[m].scored), n(nu[m].admitted), pcn(nu[m].lattice_coverage), pcn(nu[m].bipolar_coverage), n(nu[m].slope_n), f(nu[m].median_slope_error)]), [1.8, 0.8, 0.8, 1, 1, 0.9, 1])],
  populations: () => [TCAP(`Supplementary Table ${st("populations")}.`, "Experimental slope comparisons in all three populations. Paired change is relative to the reference model on the all-model-common set."),
    TABLE(["Model", "Native n", "Native C − B", "Baseline-common n", "Baseline-common C − B", "All-model-common C − B", "Paired change"],
      M.map((m) => [SH[m], n(C[m].native.n), ciB(C[m].native.CB), n(C[m].baseline_common.n), ciB(C[m].baseline_common.CB), ciB(cb(m)), m === "baseline" ? "0" : ciB(C[m].all_model_common.paired_change_CB)]),
      [1.5, 0.7, 1.6, 0.9, 1.6, 1.6, 1.6])],
  commonUpturn: () => [TCAP(`Supplementary Table ${st("commonUpturn")}.`, `Common-case narrow-gap upturn accuracy and interval width (${up.common_scored_n} curves scored by all models; slope errors on ${up.common_slope_n} curves admitted by all models). Widths in W m^{−1} K^{−1}.`),
    TABLE(["Model", "Lattice coverage (%)", "Bipolar coverage (%)", "Median lattice width", "Median slope error", "Median abs. slope error"],
      M.map((m) => { const x = up.models[m]; return [SH[m], pcn(x.lattice_coverage), pcn(x.bipolar_coverage), x.lattice_width.toFixed(3), f(x.common_slope.median_error), x.common_slope.median_absolute_error.toFixed(3)]; }), [1.8, 1, 1, 1, 1, 1])],
  mobility: () => [TCAP(`Supplementary Table ${st("mobility")}.`, "Common-case minority mobility-prefactor stress tests."),
    TABLE(["Model", "Mobility ratio", "Common scored n", "Lattice coverage (%)", "Bipolar coverage (%)"],
      [["mobility_low", "0.1"], ["mobility_high", "10"]].flatMap(([k, rv]) => M.map((m) => [SH[m], rv, n(sc[k].common_scored_n), pcn(sc[k].models[m].lattice_coverage), pcn(sc[k].models[m].bipolar_coverage)])), [1.8, 0.9, 1, 1, 1])],
  transfer: () => [TCAP(`Supplementary Table ${st("transfer")}.`, "Transfer between thermal truth models (1,000 narrow-gap curves per truth model; common inference seed 7300). Coverage is conditional on each estimator’s scored curves."),
    TABLE(["Inference model", "Truth model", "Scored / generated", "Admitted", "Lattice coverage (%)", "Bipolar coverage (%)", "Total coverage (%)"],
      M.flatMap((m) => ["mobility_extra", "mobility_spline"].map((t) => { const x = tx[m + "|" + t]; return [SH[m], SH[t], `${n(x.scored)}/${n(x.n)}`, n(x.admitted), pcn(x.lattice_coverage), pcn(x.bipolar_coverage), pcn(x.total_coverage)]; })),
      [1.6, 1.6, 1, 0.8, 0.9, 0.9, 0.9])],
  control: () => [TCAP(`Supplementary Table ${st("control")}.`, `Decreasing-lattice narrow-gap control (1,000 curves; ${nc.common_scored_n} scored by all models; slope errors on ${nc.common_slope_n} curves admitted by all models). In the reference model, ${ctl.apparent_upturn_admitted} of ${ctl.admitted} admitted curves show an apparent upturn in the conventional estimate A (index 15 above index 8) while no true lattice curve rises.`),
    TABLE(["Model", "Lattice coverage (%)", "Bipolar coverage (%)", "Median lattice width", "Median abs. slope error"],
      M.map((m) => { const x = nc.models[m]; return [SH[m], pcn(x.lattice_coverage), pcn(x.bipolar_coverage), x.lattice_width.toFixed(3), x.common_slope.median_absolute_error.toFixed(3)]; }), [1.8, 1, 1, 1, 1])],
  wide: () => [TCAP(`Supplementary Table ${st("wide")}.`, `Common-case wide-gap lattice-upturn test (inherited set, seed 2004: 1,000 curves, gaps 1.5–3.55 eV, increasing true lattice conductivity; ${wu.common_scored_n} curves scored by all models; slope errors on ${wu.common_slope_n} curves admitted by all models). Widths in W m^{−1} K^{−1}.`),
    TABLE(["Model", "Lattice coverage (%)", "Bipolar coverage (%)", "Median lattice width", "Median slope error", "Median abs. slope error"],
      M.map((m) => { const x = wu.models[m]; return [SH[m], pcn(x.lattice_coverage), pcn(x.bipolar_coverage), x.lattice_width.toFixed(3), f(x.common_slope.median_error), x.common_slope.median_absolute_error.toFixed(3)]; }), [1.8, 1, 1, 1, 1, 1])],
  scattering: () => [TCAP(`Supplementary Table ${st("scattering")}.`, "Effective-scattering classification among admitted corpus curves. Ambiguous means 0.2 ≤ *P*(*r* < 0.5) ≤ 0.8. Operational summaries of a model parameter, not identification of microscopic mechanisms."),
    TABLE(["Model", "Admitted n", "Ambiguous, majority / shared *r*", "Ambiguous, minority *r*_{min}"],
      [[SH.baseline, n(V5.admitted), n(cl.ambiguous.n), "shared parameter"]].concat(VR.map((m) => [SH[m], n(N.effective_scattering[m].r.denominator), n(N.effective_scattering[m].r.ambiguous), N.effective_scattering[m].r_min ? n(N.effective_scattering[m].r_min.ambiguous) : "shared parameter"])), [1.8, 1, 1.5, 1.5])],
  training: () => [TCAP(`Supplementary Table ${st("training")}.`, "Neural training of the extended models (588,000 training and 12,000 validation simulations each). Epochs are one-based; the selected checkpoint has the best qualifying validation loss. Single-seed runs, not replicated convergence assessments."),
    TABLE(["Model", "D", "Completed epochs", "Selected epoch", "Stop reason", "Seed"],
      VR.map((m) => { const t = N.training[m]; return [SH[m], String(N.dimension[m]), n(t.epochs_completed), n(t.selected_epoch_one_based), t.stop_reason, String(t.seed)]; }), [1.8, 0.5, 1, 1, 1, 0.8])],
  strata: () => [TCAP(`Supplementary Table ${st("strata")}.`, "C − B by inferred bipolar share at 750 K, native paired set of each model. No model has paired curves with share above 100%."),
    TABLE(["Model", "Share", "n", "Papers", "C − B [95% interval]", "C − A [95% interval]"],
      M.flatMap((m) => SKEYS.map(([l, k]) => [SH[m], l, n(st_[m][k].n), n(st_[m][k].papers), ci(st_[m][k].CB), ci(st_[m][k].CA)])), [1.8, 0.8, 0.7, 0.7, 1.7, 1.7])],
  rollover: () => [TCAP(`Supplementary Table ${st("rollover")}.`, "C − B by measured Seebeck rollover, native paired set of each model."),
    TABLE(["Model", "Rollover", "n", "Papers", "C − B [95% interval]", "C − A [95% interval]"],
      M.flatMap((m) => RK.map(([l, k]) => [SH[m], l, n(rl[m][k].n), n(rl[m][k].papers), ci(rl[m][k].CB), ci(rl[m][k].CA)])), [1.8, 0.8, 0.7, 0.7, 1.7, 1.7])],
  families: () => [TCAP(`Supplementary Table ${st("families")}.`, "Within-family C − B for families with at least 80 native paired curves in each model, including the residual “other” group. Family sets differ between models because native populations differ."),
    TABLE(["Model", "Family", "n", "Papers", "C − B [95% interval]"],
      M.flatMap((m) => Object.keys(N.families[m]).sort((a, b) => a.localeCompare(b, "en", { sensitivity: "base" })).map((k) => { const x = N.families[m][k]; return [SH[m], k, n(x.n), n(x.papers), ci(x.CB)]; })), [1.8, 1.3, 0.7, 0.7, 1.8])],
  thresholds: () => [TCAP(`Supplementary Table ${st("thresholds")}.`, "Fit-screen threshold scan: median C − B (native paired n in parentheses) at each containment threshold. The principal threshold is 0.75."),
    TABLE(["Threshold", ...M.map((m) => SH[m])],
      TH.map((t) => [t, ...M.map((m) => `${f(N.thresholds[m][t].CB[0])}\n(${n(N.thresholds[m][t].n)})`)]), [1.05, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2])],
  selection: () => [TCAP(`Supplementary Table ${st("selection")}.`, `Corpus selection and strictly negative conventional remainders (A < 0 at any grid point) by model. All models start from the same ${n(V5.n)} source-consistent records; ${n(V5.negative_A.all.n)} have a negative A somewhere in the full corpus.`),
    TABLE(["Model", "Scored", "Admitted", "Native paired", "Negative A: admitted", "Negative A: excluded", "Negative A: unscored"],
      M.map((m) => { const g = N.negative_A[m]; return [SH[m], n(sel[m].scored), n(sel[m].admitted), n(C[m].native.n), `${g.admitted.n}/${n(g.admitted.denominator)}`, `${g.excluded.n}/${n(g.excluded.denominator)}`, `${g.unscored.n}/${n(g.unscored.denominator)}`]; }),
      [1.8, 0.8, 0.8, 0.8, 1.1, 1.1, 1.1])],
};
Object.keys(SI).forEach((k) => st(k)); // uncited tables, if any, follow in list order
Object.keys(SI).sort((a, b) => st(a) - st(b)).forEach((k) => S.push(...SI[k]()));
if (Object.keys(STN).length !== Object.keys(SI).length) throw new Error("cited supplementary table key without a table: " + Object.keys(STN).filter((k) => !SI[k]));

S.push(FIGURE("supplementary_figure1_network"));
S.push(CAP("Supplementary Figure 1.", "Neural posterior estimator and training histories of the extended models. (a) Fifty standardised transport features enter three fully connected layers of 256 SiLU units; separate heads parameterise the continuous Gaussian precision and carrier-sign probability. Physical-support rejection follows neural sampling; 128 accepted draws are targeted, with at least 64 required for scoring. (b) Validation negative log likelihood minus the minimum within each run, on a symmetric logarithmic scale. Subtracting each minimum permits visual inspection of optimisation progress; it does not make likelihood values comparable across models."));
S.push(P("The separate research-data archive supplies the full per-curve inference arrays and matched draws. The source repository supplies the analysis code, compact comparison masks, numerical summaries and software provenance. Joint simulation-based calibration ranks are not supplied. Source-matched auxiliary transport data support the internal consistency checks in Supplementary Tables 31–33; they do not provide independent thermal-channel ground truth."));

// =====================================================================================
async function write(children, file) {
  const doc = new Document({ creator: "Authors", title: path.basename(file, ".docx"), styles,
    sections: [{ properties: { page }, footers: footer(), children }] });
  const JSZip = require(require.resolve("jszip", { paths: [path.dirname(require.resolve("docx")), __dirname] }));
  const zip = await JSZip.loadAsync(await Packer.toBuffer(doc));
  let xml = await zip.file("word/document.xml").async("string");
  xml = xml.replace(/<m:r>(<w:rPr>.*?<\/w:rPr>)?<m:t([^>]*)>\u2063/g, (all, rpr, attr) => `<m:r><m:rPr><m:sty m:val="p"/></m:rPr>${rpr || ""}<m:t${attr}>`);
  if (xml.includes("\u2063")) throw new Error("unconverted upright sentinel");
  zip.file("word/document.xml", xml);
  fs.writeFileSync(file, await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
  console.log("wrote", path.relative(ROOT, file));
}
(async () => {
  await write(T, path.join(OUT, "combined_manuscript.docx"));
  await write(S, path.join(OUT, "combined_supplementary_information.docx"));
})();
