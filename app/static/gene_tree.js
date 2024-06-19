function createTreeUpdated(newickData, width = 600, height = 800) {
    // Create a new phylotree
    const tree = new phylotree.phylotree(newickData);

    //Select the SVG element
    const svg = d3.select("#tree-container");

    // Clear previous content
    svg.selectAll("*").remove();

    // Set the dimensions of the SVG
    svg.attr("width", width).attr("height", height);

    // Render the tree
    renderedTree = tree.render({
        container: "#tree-container",
        height:height, 
        width:width,
        'left-right-spacing': 'fit-to-size', 
        'top-bottom-spacing': 'fit-to-size'
    })
    $(tree.display.container).html(tree.display.show());
    console.log('Rendering Tree')
    return tree;
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


