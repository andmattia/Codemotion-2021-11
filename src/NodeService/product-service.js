'use strict';

// eslint-disable-next-line
require('./tracer')('example-express-server');

// Require in rest of modules
const express = require('express');
const axios = require('axios').default;
const mongoose = require('mongoose');
const productSchema = new mongoose.Schema({
  _id: String,
  name: String,
  description: String,
  price: Number,
  country: String
});

const productDbSet = mongoose.model('Product', productSchema);

// Setup express
const app = express();
const PORT = 5000;

const getCrudController = () => {
  const router = express.Router();
  const resources = [];
  router.get('/', async (req, res) => {
    const products = await productDbSet.find();
    res.send(products);
  });
  router.get('/:productId', async (req, res) => {
    const oldProduct = await productDbSet.findById(req.params.productId).exec();
    res.send(oldProduct);
  });
  router.post('/', async (req, res) => {
    const newProduct = req.body;

    if(!mongoose.Types.ObjectId.isValid(newProduct.id))
      return res.status(400).send(req.body);

    const old = await productDbSet.findById(newProduct.id).exec();
    if(old === null) {
      const productNew = new productDbSet({
        _id: mongoose.Types.ObjectId(),
        name: newProduct.name,
        description: newProduct.description,
        price: newProduct.price,
        country: newProduct.country
      });
      await productNew.save();
    }
    else
      return res.status(409).send(old);


    return res.status(201).send(req.body);
  });
  return router;
};

app.use(express.json());
app.use('/product', getCrudController());

app.listen(PORT, () => {
  console.log(`Listening on http://localhost:${PORT}`);
});

main().catch(err => console.log(err));

async function main() {
  mongoose.connect('mongodb://mongodb:27017/productdb', {
    auth: { username: "root", password: "example" },
    authSource: "admin",
  })
    .catch(error => {
      console.log(error);
    });

  productDbSet.createCollection();
}