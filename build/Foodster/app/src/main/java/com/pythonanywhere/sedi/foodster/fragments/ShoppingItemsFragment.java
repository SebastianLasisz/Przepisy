package com.pythonanywhere.sedi.foodster.fragments;

import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.TextView;

import com.pythonanywhere.sedi.foodster.R;
import com.pythonanywhere.sedi.foodster.models.ShoppingItem;
import com.pythonanywhere.sedi.foodster.models.ShoppingList;

import org.w3c.dom.Text;

import java.util.List;

public class ShoppingItemsFragment extends Fragment {

    private ShoppingList sl;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_shopping_items, container, false);
        LinearLayout mainLayout = (LinearLayout) view.findViewById(R.id.items_layout);

        if(sl != null) {
            TextView description = (TextView) view.findViewById(R.id.descriptionView);
            description.setText(sl.getDescription());

            List<ShoppingItem> items = sl.getItems();
            for (ShoppingItem item : items) {


                View shopping_item = inflater.inflate(R.layout.shopping_item, null);

                TextView item_name = (TextView) shopping_item.findViewById(R.id.item_name);
                item_name.setText(item.getName());

                TextView item_value = (TextView) shopping_item.findViewById(R.id.item_value);
                item_value.setText(Float.toString(item.getValue()));

                TextView item_unit = (TextView) shopping_item.findViewById(R.id.item_unit);
                item_unit.setText(item.getUnit());

                mainLayout.addView(shopping_item);

            }
        }

        return view;
    }

    public void setShoppingList(ShoppingList sl){
        this.sl = sl;
    }

}
