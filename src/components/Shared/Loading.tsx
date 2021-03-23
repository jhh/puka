import React, { useEffect, useState } from "react";

const useDelayedRender = (delay: number) => {
  const [delayed, setDelayed] = useState(true);
  useEffect(() => {
    const timeout = setTimeout(() => setDelayed(false), delay);
    return () => clearTimeout(timeout);
  }, [delay]);
  return (elt: () => any) => !delayed && elt();
};

type DelayedRenderProps = {
  delay: number;
  children: React.ReactNode;
};

const DelayedRender = ({ delay, children }: DelayedRenderProps) =>
  useDelayedRender(delay)(() => children);

const Loading = () => {
  const classes = {
    centered: "centered",
  };

  return (
    <DelayedRender delay={800}>
      <div className={classes.centered}>Loading</div>
    </DelayedRender>
  );
};

// const useStyles = makeStyles((theme) => ({
//   root: {
//     width: "100vw",
//     textAlign: "center",
//   },
//   progress: {
//     color: theme.palette.secondary.dark,
//   },
//   centered: {
//     color: theme.palette.secondary.dark,
//     position: "fixed",
//     top: "50%",
//     left: "50%",
//     marginTop: "-50px",
//     marginLeft: "-50px",
//   },
// }));

export default Loading;
