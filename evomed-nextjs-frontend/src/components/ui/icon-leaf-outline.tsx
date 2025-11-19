import React, {SVGProps} from 'react';

export interface IconProps extends React.SVGProps<SVGSVGElement> {
  strokeWidth?: number;
  size?: string;
}

function IconLeafOutline18({strokeWidth = 1.5, size = '18px', ...props}: IconProps) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" x="0px" y="0px" width={size} height={size} viewBox="0 0 18 18" {...props}><path d="m9.8997,15.1642c4.9614-.879,6.1773-8.293,3.3653-13.4142-1.709,3.571-5.652,3.034-7.858,5.754-.654.806-1.158,1.901-1.158,3.082,0,1.577.779,2.972,1.972,3.816" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth={strokeWidth}></path><path d="m2.75,16.25s4.598-1.265,7.5-6.5" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth={strokeWidth} data-color="color-2"></path></svg>
  );
};

export default IconLeafOutline18;
