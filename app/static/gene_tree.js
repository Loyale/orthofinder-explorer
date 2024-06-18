
function createTreeDeprecated(newickData) {
    var example_tree = "(((EELA:0.150276,CONGERA:0.213019):0.230956,(EELB:0.263487,CONGERB:0.202633):0.246917):0.094785,((CAVEFISH:0.451027,(GOLDFISH:0.340495,ZEBRAFISH:0.390163):0.220565):0.067778,((((((NSAM:0.008113,NARG:0.014065):0.052991,SPUN:0.061003,(SMIC:0.027806,SDIA:0.015298,SXAN:0.046873):0.046977):0.009822,(NAUR:0.081298,(SSPI:0.023876,STIE:0.013652):0.058179):0.091775):0.073346,(MVIO:0.012271,MBER:0.039798):0.178835):0.147992,((BFNKILLIFISH:0.317455,(ONIL:0.029217,XCAU:0.084388):0.201166):0.055908,THORNYHEAD:0.252481):0.061905):0.157214,LAMPFISH:0.717196,((SCABBARDA:0.189684,SCABBARDB:0.362015):0.282263,((VIPERFISH:0.318217,BLACKDRAGON:0.109912):0.123642,LOOSEJAW:0.397100):0.287152):0.140663):0.206729):0.222485,(COELACANTH:0.558103,((CLAWEDFROG:0.441842,SALAMANDER:0.299607):0.135307,((CHAMELEON:0.771665,((PIGEON:0.150909,CHICKEN:0.172733):0.082163,ZEBRAFINCH:0.099172):0.272338):0.014055,((BOVINE:0.167569,DOLPHIN:0.157450):0.104783,ELEPHANT:0.166557):0.367205):0.050892):0.114731):0.295021)"
    //print tree data to console (for testing)
    //console.log(newickData);
    var tree = d3.layout.phylotree()
        // create a tree layout object
        .svg(d3.select("#tree-container"));

    // render to this SVG element
    tree(d3.layout.newick_parser(newickData)).layout();
    //tree(d3.layout.newick_parser(example_tree)).layout();
    // layout and render the tree
}

function createTree(newickData, width=600) {
    // Clear the existing tree if present
    //d3.select("#tree-container").html("");

    // Initialize the phylotree
    var tree = new d3.layout.phylotree()
        .svg(d3.select("#tree-container"));
        
    tree(d3.layout.newick_parser(newickData)).layout();

    // Update the SVG width
    d3.select("#tree-container svg")
        .attr("width", width)
        .attr("height", tree.size()[1]);

    // Apply styling to the tree
    // tree.style_edges(function(element, data) {
    //     d3.select(element).style("stroke", "black");
    // });

    // tree.style_nodes(function(element, data) {
    //     d3.select(element).select("text").style("font-size", 50);
    // });
    
    tree.get_nodes().forEach (function (tree_node) {
        //console.log(tree_node);
        //tree_node.style("color","red")
    });
    
    $(".phylotree-layout-mode").on ("change", function (e) {
        if ($(this).is(':checked')) {
            if (tree.radial () != ($(this).data ("mode") == "radial")) {
                tree.radial (!tree.radial ()).placenodes().update ();
            }
        }
    });
    return tree;
};


