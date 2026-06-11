import React from 'react';

interface KeepAliveProps {
  active: boolean;
  children: React.ReactNode;
}

const KeepAlive: React.FC<KeepAliveProps> = React.memo(({ active, children }) => {
  const [hasActivated, setHasActivated] = React.useState(active);

  React.useEffect(() => {
    if (active) {
      setHasActivated(true);
    }
  }, [active]);

  if (!hasActivated) {
    return null;
  }

  return (
    <div
      aria-hidden={!active}
      style={active
        ? { display: 'block' }
        : {
          position: 'absolute',
          inset: 0,
          width: '100%',
          visibility: 'hidden',
          pointerEvents: 'none',
          zIndex: -1,
        }}
    >
      {children}
    </div>
  );
});

KeepAlive.displayName = 'KeepAlive';

export default KeepAlive;
