package com.pythonanywhere.sedi.foodster.models;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

public class ShoppingList {

    private String name;
    private String description;
    private List<ShoppingItem> items;

    public ShoppingList(String name, String description){
        this.name = name;
        this.description = description;
        items = new ArrayList<ShoppingItem>();
    }

    public List<ShoppingItem> getItems(){
        return items;
    }

    public void addItem(JSONObject item) throws JSONException {
        JSONObject unit = item.getJSONObject("unit");
        JSONObject product = item.getJSONObject("product");
        items.add(new ShoppingItem(product.getString("name"), Float.parseFloat(item.getString("quantity")), unit.getString("abbreviation")));
    }

    public String getName(){
        return name;
    }

    public String getDescription(){
        return description;
    }
}
