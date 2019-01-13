
const webpack = require('webpack');
const helpers = require('./helpers');

// problem with copy-webpack-plugin
const AssetsPlugin = require('assets-webpack-plugin');
const ContextReplacementPlugin = require('webpack/lib/ContextReplacementPlugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const loader = require('awesome-typescript-loader')
const HtmlWebpackPlugin = require('html-webpack-plugin');
const LoaderOptionsPlugin = require('webpack/lib/LoaderOptionsPlugin');
const ScriptExtHtmlWebpackPlugin = require('script-ext-html-webpack-plugin');

module.exports = function (options) {
  isProd = options.env === 'production';
  return {

    entry: {
      'polyfills': './src/polyfills.browser.ts',
      'vendor': './src/vendor.browser.ts',
      'main': './src/main.browser.ts'
    },

    resolve: {
      extensions: ['.ts', '.js', '.json'],

      // An array of directory names to be resolved to the current directory
     // modules: [helpers.root('src'), 'node_modules'],
    },
    optimization: {
      runtimeChunk: true,
      splitChunks: {
          chunks: "initial",
          cacheGroups: {
              default: false,
              vendors: false,
          },
      },
  },

    module: {
      rules: [
        {
          test: /\.ts$/,
          loaders: [
            'awesome-typescript-loader',
            'angular2-template-loader'
          ]
        },
        {
          test: /\.json$/,
          loader: 'json-loader',
           exclude: '/node_modules/'
        },
        {
          test: /\.css$/,
          loaders: ['to-string-loader', 'css-loader'],
           exclude: '/node_modules/'
        },
         { 
           test: /bootstrap\/dist\/js\/umd\//,
           loader: 'imports?jQuery=jquery' 
        },
        {
          test: /\.(sass|scss)$/,
          loader: ['raw-loader', 'sass-loader']
        },
        { 
          test: /\.woff/, 
          loader: 'url-loader?limit=10000&minetype=application/font-woff' ,
           exclude: '/node_modules/'
        },
        { 
          test: /\.(ttf|eot|svg)/, 
          loader: 'file-loader' ,
           exclude: '/node_modules/'
        },
        {
          test: /\.html$/,
          loader: 'raw-loader',
          exclude: [helpers.root('src/index.html'), /node_modules/],
        },

        {
          test: /\.(jpg|png|gif)$/,
          loader: 'file-loader',
           exclude: /node_modules/
        },
      ],
    },
    plugins: [
      new webpack.ProvidePlugin({   
        jQuery: 'jquery',
        $: 'jquery',
        jquery: 'jquery'
      }),
      new AssetsPlugin({
        path: helpers.root('dist'),
        filename: 'webpack-assets.json',
        prettyPrint: true
      }),

      new loader.CheckerPlugin(),
    
      new ContextReplacementPlugin(
        // The (\\|\/) piece accounts for path separators in *nix and Windows
        /angular(\\|\/)core(\\|\/)(esm(\\|\/)src|src)(\\|\/)linker/,
        helpers.root('src') // location of your src
      ),
      new CopyWebpackPlugin([{
        from: 'src/assets',
        to: 'assets',
      } ]),
      new HtmlWebpackPlugin({
        template: 'src/index.html',
       // title: METADATA.title,
        chunksSortMode: 'dependency',
       // metadata: METADATA,
        inject: 'head'
      }),
      new ScriptExtHtmlWebpackPlugin({
        defaultAttribute: 'defer'
      }),
      new LoaderOptionsPlugin({}),
    ],

    node: {
      global: true,
      crypto: 'empty',
      process: true,
      module: false,
      clearImmediate: false,
      setImmediate: false
    }

  };
}
