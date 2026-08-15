const renderMermaid = async () => {
  const { default: mermaid } = await import("https://unpkg.com/mermaid@10/dist/mermaid.esm.min.mjs");

  mermaid.initialize({
    startOnLoad: false,
    theme: "base",
    securityLevel: "loose",
    flowchart: { useMaxWidth: true, htmlLabels: true },
    themeVariables: {
      background: "#ffffff",
      primaryColor: "#e8edfa",
      primaryTextColor: "#101b35",
      primaryBorderColor: "#52698f",
      secondaryColor: "#e1f4f7",
      tertiaryColor: "#f1edff",
      lineColor: "#52698f",
      clusterBkg: "#f8f9fc",
      clusterBorder: "#b8c2d7",
      edgeLabelBackground: "#ffffff",
      fontFamily: "Inter, system-ui, sans-serif",
    },
  });

  await mermaid.run({ nodes: document.querySelectorAll(".mermaid") });
  document.querySelectorAll(".mermaid svg .node, .mermaid svg .cluster").forEach((node) => {
    const shape = node.querySelector("rect, path, polygon");
    if (!shape) return;

    const rgb = getComputedStyle(shape).fill.match(/\d+/g);
    if (!rgb) return;

    const [red, green, blue] = rgb.map(Number).map((value) => {
      const channel = value / 255;
      return channel <= 0.04045 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4;
    });
    const luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue;
    const labelColor = luminance > 0.38 ? "#101b35" : "#ffffff";

    node.querySelectorAll("text, .label, .nodeLabel, foreignObject div, foreignObject span").forEach((label) => {
      label.style.setProperty("color", labelColor, "important");
      label.style.setProperty("fill", labelColor, "important");
    });
  });
};

document$.subscribe(renderMermaid);
