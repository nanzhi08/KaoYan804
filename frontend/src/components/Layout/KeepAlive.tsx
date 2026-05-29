import React from 'react';

interface KeepAliveProps {
  active: boolean;
  children: React.ReactNode;
}

/**
 * KeepAlive container - hides inactive children via display:none
 * instead of unmounting them, preserving all React + DOM state.
 */
const KeepAlive: React.FC<KeepAliveProps> = React.memo(({ active, children }) => {
  return (
    <div style={{ display: active ? 'block' : 'none' }}>
      {children}
    </div>
  );
});

KeepAlive.displayName = 'KeepAlive';

export default KeepAlive;
