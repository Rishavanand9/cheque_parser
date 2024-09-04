import React, { useRef, useEffect } from 'react';
import * as d3 from 'd3';
import styled from 'styled-components';

const SVGContainer = styled.div`
  width: 100%;
  height: 400px;
  overflow: auto;
`;

const ImageDisplay = ({ imageData }) => {
  const svgRef = useRef(null);

  useEffect(() => {
    if (imageData) {
      const svg = d3.select(svgRef.current);
      svg.selectAll("*").remove();

      const width = 1000;
      const height = 600;

      svg
        .attr("width", width)
        .attr("height", height)
        .style("border", "1px solid #ccc");

      svg.append("image")
        .attr("xlink:href", `data:image/jpeg;base64,${imageData}`)
        .attr("width", width)
        .attr("height", height);
    }
  }, [imageData]);

  return (
    <SVGContainer>
      <svg ref={svgRef}></svg>
    </SVGContainer>
  );
};

export default ImageDisplay;