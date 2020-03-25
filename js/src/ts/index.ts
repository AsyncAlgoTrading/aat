import perspective from "@finos/perspective";
// import {PerspectiveViewerWidget, PerspectiveWorkspace} from "@finos/perspective-workspace";
import {DockPanel, Widget} from "@lumino/widgets";

import "@finos/perspective-viewer";
import "@finos/perspective-viewer-datagrid";
import "@finos/perspective-viewer-d3fc";
import "@finos/perspective-viewer-hypergrid";
import "@finos/perspective-viewer/themes/material-dense.dark.css";
import "!!style-loader!css-loader!less-loader!../src/style/index.less";


document.addEventListener("WebComponentsReady", async () => {
    const tradesViewer = document.createElement("perspective-viewer");
    tradesViewer.restore({
        plugin: "datagrid",
        sort: [["timestamp", "asc"]],
    });

    const ordersViewer = document.createElement("perspective-viewer");
    ordersViewer.restore({
        plugin: "datagrid",
        "column-pivots": ["side"],
        sort: [["price", "desc"]],
    });

    // connect to perspective
    const websocket = perspective.websocket("ws://localhost:8080/api/v1/ws");

    const tradesTable = websocket.open_table("trades");
    const ordersTable = websocket.open_table("orders");

    // perspective workspace
    // const workspace = new PerspectiveWorkspace();
    // workspace.addClass("workspace");
    // workspace.title.label = "AAT";
    const workspace = new DockPanel();
    workspace.addClass("workspace");

    // const tradesWidget = new PerspectiveViewerWidget("Trades");
    // const ordersWidget = new PerspectiveViewerWidget("Orders");

    // Add tables to workspace
    const tradesWidget = new Widget({node: tradesViewer});
    const ordersWidget = new Widget({node: ordersViewer});
    workspace.addWidget(tradesWidget, {});
    workspace.addWidget(ordersWidget, {mode: "split-bottom", ref: tradesWidget});

    // Attach parts to dom
    Widget.attach(workspace, document.body);

    // Load perspective tables
    tradesViewer.load(tradesTable);
    ordersViewer.load(ordersTable);

    // (window as any).workspace = workspace;
});
