package com.pythonanywhere.sedi.foodster.models;

public class ShoppingItem {

    private String name;
    private float value;
    private String unit;

    public ShoppingItem(String name, float value, String unit){
        this.name = name;
        this.value = value;
        this.unit = unit;
    }

    public String getName(){
        return name;
    }

    public float getValue(){
        return value;
    }

    public String getUnit(){
        return unit;
    }

}
