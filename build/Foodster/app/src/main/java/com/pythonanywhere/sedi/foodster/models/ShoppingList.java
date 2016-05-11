package com.pythonanywhere.sedi.foodster.models;

import java.util.ArrayList;
import java.util.List;

public class ShoppingList {

    private String name;
    private String description;
    private List<String> items;

    public ShoppingList(String name, String description){
        this.name = name;
        this.description = description;
        items = new ArrayList<String>();
    }

    public List<String> getItems(){
        return items;
    }

    public void addItem(String item){
        items.add(item);
    }

    public String getName(){
        return name;
    }

    public String getDescription(){
        return description;
    }
}
