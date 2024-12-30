const path = require('path');

module.exports = {
  entry: './src/index.js', // Entry point for your JavaScript
  output: {
    filename: 'bundle.js', // Output file name
    path: path.resolve(__dirname, 'static/js/dist'), // Output directory
  },
  module: {
    rules: [
      {
        test: /\.css$/, // Apply the following loaders for CSS files
        use: ['style-loader', 'css-loader'],
      },
    ],
  },
  mode: 'development', // Development mode (use 'production' for production)
  devtool: 'source-map', // Enable source maps for easier debugging
};
