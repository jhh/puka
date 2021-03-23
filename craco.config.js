const CracoAntDesignPlugin = require("craco-antd");
const path = require("path");

module.exports = {
  plugins: [
    {
      plugin: CracoAntDesignPlugin,
      options: {
        lessLoaderOptions: {
          lessOptions: {
            modifyVars: {
              // "@primary-color": "#1DA57A",
            },
            javascriptEnabled: true,
          },
        },
        cssLoaderOptions: {
          modules: {
            auto: /src/, // don't process antd Less files
            localIdentName:
              process.env.NODE_ENV === "development"
                ? "[path][name]__[local]"
                : "[hash:base64]",
            localIdentContext: path.resolve(__dirname, "src"),
          },
        },
      },
    },
  ],
};
