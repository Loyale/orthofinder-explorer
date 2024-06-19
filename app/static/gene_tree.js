//const { selection } = require("d3");

function createTreeUpdated(newickData, width = 600, height = 800) {
    // Create a new phylotree
    const tree = new phylotree.phylotree(newickData);

    //Select the SVG element
    const svg = d3.select("#tree-container");

    // Clear previous content
    svg.selectAll("*").remove();

    // Set the dimensions of the SVG
    svg.attr("width", width).attr("height", height);

    // Get an array of all genus names from node names.split("_")[0]
    getGenusNames = function (nodeData) {
        let selection_set = new Set();

        nodeData.forEach( function(d,i) {
            selection_set.add(d.data.name.split ("_")[0]);
        })
        return Array.from(selection_set);
    };

    selection_set = getGenusNames(tree.getTips());
    console.log(selection_set);


    // Color by genus
    color_scale = d3.scaleOrdinal(d3.schemeCategory10);
    //selection_set = tree.get_parsed_tags().length > 0 ? tree.get_parsed_tags() : ["Octopus","Salmo","Danio","Homo","Mus"];
    nodeColorizer = function (element, data) {
        try{
            var count_class = 0;
        
            selection_set.forEach (function (d,i) { if (data.data.name.startsWith(d)) { count_class ++; element.style ("fill", color_scale(i), 'important');}});
            if (count_class > 1) {
        
            } else {
                if (count_class == 0) {
                    element.style ("fill", null);
                }
            }
        }
        catch (e) {
        
        }
        };

    colorNodesByName = function (element, data) {
        nodeColorizer (element, data);
        var m = (data.data.name).split ("_");
        if (m.length > 10) {
            element.style ("stroke", color_scale(_.lowerCase(m[9])));
        }
    };

    // Render the tree
    renderedTree = tree.render({
        container: "#tree-container",
        height:height, 
        width:width,
        'left-right-spacing': 'fit-to-size', 
        'top-bottom-spacing': 'fit-to-size',
        'node-styler': colorNodesByName,
        'align-tips':true,
        'zoom':false,
        'show-scale':true,
    })

    $(tree.display.container).html(tree.display.show());
    //console.log('Rendering Tree')
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


