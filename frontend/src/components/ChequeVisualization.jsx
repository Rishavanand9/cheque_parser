import React, { useEffect } from 'react';
import * as d3 from 'd3';

export const ChequeVisualization = ({ 
  svgRef, 
  result, 
  fieldConfig, 
  fields, 
  handleFieldChange, 
  inputRefs 
}) => {
    
  useEffect(() => {
    if (result && result.image_data) {
      const svg = d3.select(svgRef.current);
      svg.selectAll("*").remove();

      const width = 1000;
      const height = 500;

      svg
        .attr("width", width)
        .attr("height", height)
        .style("border", "1px solid #ccc");

      // Create an image element
      svg.append("image")
        .attr("xlink:href", `data:image/jpeg;base64,${result.image_data}`)
        .attr("width", width)
        .attr("height", 400);

      // Add dots, labels, and input fields for each field
      Object.entries(fieldConfig).forEach(([field, config]) => {
        // Add dot on the cheque
        svg.append("circle")
          .attr("cx", config.x)
          .attr("cy", config.y)
          .attr("r", 5)
          .attr("fill", config.color);

        // Add label
        svg.append("text")
          .attr("x", config.x)
          .attr("y", config.y + 8)
          .text(config.label)
          .style("font-size", "10px")
          .style("font-weight", "bold")
          .style("fill", config.color)
          .style("text-anchor", "middle");

        // Add input field
        const foreignObject = svg.append("foreignObject")
          .attr("x", config.x - 75)
          .attr("y", config.y + 10)
          .attr("width", 230)
          .attr("height", 40);

        const input = foreignObject.append("xhtml:input")
          .attr("type", "text")
          .attr("value", fields?.[field]?.['value'] || '')
          .style("width", "100%")
          .style("height", "100%")
          .style("font-size", "12px")
          .style("padding", "2px 8px")
          .style("color", 'white')
          .style("background-color", "rgba(0, 0, 0, 0.7)")
          .style("border", `2px solid ${config.color}`)
          .style("transition", "background-color 0.3s");

        input.on("input", function() {
          handleFieldChange(field, this.value);
        });

        // Store reference to the input element
        inputRefs.current[field] = input.node();
      });
    }
    // eslint-disable-next-line
  }, [result, fieldConfig, fields, handleFieldChange]);

  return (
    <div className="card image-section">
      <svg ref={svgRef}></svg>
    </div>
  );
};
